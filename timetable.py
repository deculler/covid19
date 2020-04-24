from datascience import Table, Formatter, PercentFormatter
import numpy as np
from scipy.interpolate import UnivariateSpline, interp1d
import matplotlib.pyplot as plots

class TimeTable(Table):
    """Table with a designated column as a sequence of times in the first column.
    optionally, time_less provide comparison of times.
    """

    def __init__(self, *args, time_column = 'Day', time_less = None, time_inc = None):
        Table.__init__(self, *args)
        self.time_column = time_column
        self.time_less = time_less
        self.time_inc = time_inc
        
    @property
    def categories(self):
        return [label for label in self.labels if label != self.time_column]
    
    @classmethod
    def from_table(cls, tbl, time_col, time_less_fun = None, time_inc_fun = None):
        """ Construct a TimeTable from a Table """

        ttbl = cls(time_column = time_col, time_less = time_less_fun, time_inc = time_inc_fun)
        for label in tbl.labels:
            ttbl[label] = tbl[label]
        return ttbl
    
    @classmethod
    def by_time(cls, tbl, time_col, category_col, collect_col, collect=sum,
                     time_less_fun = None, time_inc_fun = None):
        """Construct a time table by aggregating rows of each category by time bins."""

        tbl_by_time = tbl.select([category_col, time_col, collect_col]).pivot(category_col, time_col, 
                                                                              collect_col, collect=collect)
        return cls(tbl_by_time.labels,
                   time_column = time_col,
                   time_less   = time_less_fun,
                   time_inc    = time_inc_fun).append(tbl_by_time)
    
    @classmethod
    def transpose(cls, tbl, category_col, time_col='Day', time_less = None, time_inc = None) :
        """Transpose a table with one column containing categories and remaining labels time stamps"""

        time_col_vals = [lbl for lbl in tbl.labels if not lbl == category_col]
        xtbl = Table().with_column(time_col, time_col_vals)
        vals = tbl.drop(category_col)
        for lbl, vals in zip(tbl[category_col], vals.rows) :
            xtbl[lbl] = vals
        return TimeTable.from_table(xtbl, time_col, time_less, time_inc)
    
    # Functional Table methods produce a new object.  Need to set time_column attribute

    def _fix_(self, t):
        """Retain TimeTable attributes across functional Table methods."""
        if self.time_column in t.labels :
            return self.from_table(t, self.time_column, self.time_less, self.time_inc)
        else :
            return Table.copy(t)

    def read_table(self, *args, **kwargs):
        return self._fix_(Table.read_table(*args, **kwargs))
    
    def with_column(self, label, values):
        return self._fix_(Table.with_column(self, label, values))
    
    def with_columns(self, *labels_and_values, **formatter):
        return self._fix_(Table().with_columns(*labels_and_values, **formatter))
    
    """
    def with_row(self, *args, **kwargs):
        return self._fix_(Table.with_row(*args, **kwargs))
    
    def with_rows(self, *args, **kwargs):
        return self._fix_(Table.with_rows(*args, **kwargs))
    """
    
    def copy(self, *args, **kwargs):
        return self._fix_(Table.copy(self, *args, **kwargs))
    
    def select(self, *args, **kwargs):
        return self._fix_(Table.select(self, *args, **kwargs))

    def drop(self, *args, **kwargs):
        return self._fix_(Table.drop(self, *args, **kwargs))
    
    def take(self, *args, **kwargs):
        return self._fix_(Table.take(self, *args, **kwargs))

    def exclude(self, *args, **kwargs):
        return self._fix_(Table.exclude(self, *args, **kwargs))

    def move_column(self, *args, **kwargs):
        return self._fix_(Table.move_column(self, *args, **kwargs))

    def where(self, *args, **kwargs):
        return self._fix_(Table.where(self, *args, **kwargs))

    def sort(self, *args, **kwargs):
        return self._fix_(Table.sort(self, *args, **kwargs))
    
    def join(self, *args, **kwargs):
        return self._fix_(Table.join(self, *args, **kwargs))
    
    

    def __get_attr__(self, name):
        def wrapper(*args, **kwargs):
            # Wrap superclass method to coerce result back to TimeTable
            tbl = self.name(*args, **kwargs)
            if isinstance(tbl, Table) and self.time_column in tbl.labels:
                return TimeTable.from_table(tbl, self.time_column)
            else:
                return tbl
        print("Get TimeTable Attr", name)
        if hasattr(Table, name):
            return wrapper
        else:
            raise AttributeError
            
    def get(self, time_val, col):
        return self.where(self.time_column, time_val).last(col)
    
    def extract(self, column_or_columns):
        """Select catagories along with time column"""
        labels = self._varargs_as_labels(column_or_columns)
        if not self.time_column in labels:
            labels = [self.time_column] + labels
        return self.select(labels)
    
    def after(self, time_val):
        """Return TimeTable of rows after time_val, inclusive."""
        if self.time_less :
            return self.where(self.apply(lambda t: not self.time_less(t, time_val), self.time_column))
        else :
            return self.where(self.apply(lambda t: t >= time_val , self.time_column))

    def before(self, time_val):
        """Return TimeTable of rows up to time_val, inclusive."""
        if self.time_less :
            return self.where(self.apply(lambda t: not self.time_less(time_val, t), self.time_column))
        else :
            return self.where(self.apply(lambda t: t <= time_val , self.time_column))

    def between(self, time_start, time_end):
        """Return TimeTable of rows between time_val."""
        return self.after(time_start).before(time_end)
    
    def tail(self, prev, time_end=None):
        """Return TimeTable of prev rows prior to time_end, defaults to last."""
        if not time_end :
            time_end = self.last(self.time_column)
        elif isinstance(time_end, int):
            time_end = self.time_inc(self.last(self.time_column), -time_end)
        return self.between(self.time_inc(time_end, -prev), time_end)
        
    # TimeTable methods utilizing time_column
    
    def snap(self, times, fcol=None):
        """Snap TimeTable to points in times, interpolate 0 points in fcol, if specified."""
        sttbl = TimeTable([self.time_column])
        sttbl[self.time_column] = times
        if fcol :
            ftbl = self.where(fcol)
        else :
            ftbl = self.copy()
        otimes = ftbl[self.time_column]
        for col in ftbl.categories :
            # the interpolation function returned by 'interp1d' cannot use any NaN
            # values. 'not_nan' contains the indexes of 'good' values; we use this
            # to index into the X values (otimes) and Y values (ftbl[col]) so that
            # interp1d only sees non-nan values
            not_nan = np.where(np.isfinite(ftbl[col]))
            f = interp1d(otimes[not_nan], ftbl[col][not_nan], fill_value = 'extrapolate')
            sttbl[col] = f(times)
        return sttbl

    def order_cols(self):
        """Create a TimeTable with categories ordered by the values in last row."""
        def col_key(label):
            return self.last(label)
        order = sorted(self.categories, key=col_key, reverse=True)
        tbl = self.copy()
        for label in order:
            tbl.move_to_end(label)
        return tbl
    
    def oplot(self, rotation=90, xlab=None, **kwargs):
        ocols = self.order_cols()
        ocols.plot(self.time_column, **kwargs)
        _ = plots.xticks(rotation=rotation)
        if xlab and ocols.num_rows > xlab :
            ocols.plots[-1].xaxis.set_major_locator(plots.MaxNLocator(xlab))
        return
    
    def obar(self, **kwargs):
        return self.order_cols().bar(self.time_column, **kwargs)
    
    def top(self, n):
        """Create a new TimeTable containing the n largest columns."""
        ttbl = self.order_cols()
        return ttbl.select(range(n+1))
    
    def sum_rows(self):
        """Sum the rows in a TimeTable besides the time column."""
        tbl = self.drop(self.time_column)
        return [sum(row) for row in tbl.rows]
    
    def cumsum(self):
        """Cumulative sum of columns in TimeTable"""
        cum = self.copy()
        for ncol in range(2, self.num_columns) :
            lbl = cum.labels[ncol]
            cum[lbl] = cum[ncol-1] + cum[ncol]
        return cum
    
    def apply_cols(self, fun):
        """Apply a function to the non-time columns of TimeTable."""
        return Table().with_columns([(lbl, fun(self[lbl])) for lbl in self.categories])
    
    def apply_all(self, fun):
        ttbl = TimeTable(time_column = self.time_column)
        for lbl in self.labels:
            if lbl == self.time_column:
                ttbl[lbl] = self[self.time_column]
            else:
                ttbl[lbl] = self.apply(fun, lbl)
        return ttbl
   
    def ratio(self, tbl_denom):
        """Create ratio of a TimeTable to a matching one."""
        rtbl = TimeTable(time_column = self.time_column).with_column(self.time_column, self[self.time_column])
        for label in self.categories:
            rtbl[label] = self[label] / tbl_denom[label]
        return rtbl
    
    def normalize(self, col_label):
        """Normalize each column of a timetable by a particular one"""
        rtbl = TimeTable(time_column = self.time_column).with_column(self.time_column, self[self.time_column])
        for label in self.categories:
            rtbl[label] = self[label] / self[col_label]
        return rtbl
    
    def delta(self):
        """Construct a TimeTableable of successive differences down each non-time column."""
        delta_tbl = self.clone_bare()
        delta_tbl[self.time_column] = self[self.time_column][1:]
        for col in self.categories:
            delta_tbl[col] = self[col][1:] - self[col][:-1]
        return delta_tbl
    
    def fill(self, interval=1):
        times = [t for t in np.arange(self[self.time_column][0], self[self.time_column][-1] + interval, interval)]
        ftbl = TimeTable(time_column = self.time_column).with_column(self.time_column, times)
        for col in self.categories:
            spl = UnivariateSpline(self[self.time_column], self[col])
            ftbl[col] = spl(times)
        return ftbl
    
    def interp(self, interval=1):
        times = [t for t in np.arange(self[self.time_column][0], self[self.time_column][-1] + interval, interval)]
        ftbl = TimeTable(time_column = self.time_column).with_column(self.time_column, times)
        for col in self.categories:
            ftbl[col] = np.interp(times, self[self.time_column], self[col])
        return ftbl

    def rel_delta(self):
        """Construct a TimeTableable of successive differences down each non-time column."""
        delta_tbl = self.clone_bare()
        delta_tbl[self.time_column] = self[self.time_column][1:]
        time_delta = self[self.time_column][1:] - self[self.time_column][:-1]
        for col in self.categories:
            delta_tbl[col] = (1+(self[col][1:] - self[col][:-1])/self[col][:-1])/time_delta
        return delta_tbl
    
    def norm_by_row(self, base_row=0):
        """Normalize columns of a TimeTable by a row"""
        normed_tbl = self.clone_time()
        for label in self.categories:
            normed_tbl[label] = self[label]/self[label][base_row]
        return normed_tbl
    
    def norm_by_time(self, time):
        return self.norm_by_row(np.where(self[self.time_column] == time)[0][0])
    
    def sum_cols(self):
        """Sum the columns of TimeTable."""
        csum = 0
        for c in self.categories:
            csum += self[c]
        return csum
    
    def fraction_cols(self):
        """Convert each column to a fraction by row."""
        total = self.sum_cols()
        ftbl = self.clone_time()
        for lbl in self.categories:
            ftbl[lbl] = self[lbl]/total
        return ftbl
    
    def forecast_table(self, past, ahead, inc=1):
        """Project a TimeTable forward.  inc must match the interval"""
        last_time = self[self.time_column][-1]
        past_times = self[self.time_column][-past-1:-1]
        fore_time = np.arange(last_time + inc, last_time + inc + ahead, inc)
        def project(lbl):
            m, b = np.polyfit(past_times, self[lbl][-past-1:-1], 1)
            return [m*time + b for time in fore_time]
        xtbl = Table().with_columns([(self.time_column, fore_time)] + [(label, project(label)) for label in self.categories])
        return self.copy().append(xtbl)
    
    def extend_table(self, ahead, inc=1):
        """Project a TimeTable forward from last interval.  inc must match the interval"""
        last_time = self[self.time_column][-1]
        fore_time = np.arange(last_time + inc, last_time + inc + ahead, inc)
        def project(lbl):
            b = self[lbl][-1]
            m = self[lbl][-1] - self[lbl][-2]
            return [m*(time+1)*inc + b for time in range(ahead)]
                                             
        xtbl = Table().with_columns([(self.time_column, fore_time)] + [(label, project(label)) for label in self.categories])
        return self.copy().append(xtbl)
    
    def add_table(self, ttbl):
        """Sum columns of time tables in matching categories"""
        assert self.time_column == ttbl.time_column
        assert np.array_equal(self[self.time_column], ttbl[ttbl.time_column])
        cat, tcat = self.categories, ttbl.categories
        atbl = self.copy()
        for lbl in cat :
            if lbl in tcat :
                atbl[lbl] += ttbl[lbl]
        for lbl in tcat :
            if lbl not in cat :
                atbl[lbl] = ttbl[lbl]
        return atbl
    
    def trend(self, active=True, active_distance=14):
        """Return TimeTable with trends for each time series."""
        ttbl = self.select(self.time_column)
        with np.errstate(divide='ignore', invalid='ignore'):
            if len(self.categories) == 1 :
                name = self.categories[0]
                ttbl[name] = self[name]
                ttbl['new'] = [np.nan] + list(self[name][1:] - self[name][:-1])
                ttbl['% new'] = ttbl['new'] / (ttbl[name] - ttbl['new'])
                ttbl.set_format('% new', PercentFormatter)
                ttbl['rate'] = [np.nan] + list(self[name][1:] / self[name][:-1])
                if active :
                    ttbl['active'] = [np.nansum(ttbl['new'][max(0,i-active_distance) : i+1]) for i in range(ttbl.num_rows)]
                    ttbl['arate'] = ttbl['new'] / ttbl['active']
            else :
                for name in self.categories :
                    ttbl[name] = self[name]
                    newname = 'new ' + name
                    pername = '%new ' + name
                    ratename = 'rate ' + name
                    actname = 'active ' + name
                    aratename = 'arate ' + name
                    ttbl[newname] = [np.nan] + list(self[name][1:] - self[name][:-1])
                    ttbl[pername] = np.divide(ttbl[newname], ttbl[name])
                    ttbl.set_format(pername, PercentFormatter)
                    ttbl[ratename] = [np.nan] + list(np.divide(self[name][1:], self[name][:-1]))
                    if active :
                        ttbl[actname] = [np.nansum(ttbl[newname][max(0,i-active_distance) : i+1]) for i in range(ttbl.num_rows)]
                        ttbl[aratename] = ttbl[newname] / ttbl[actname]
        return ttbl
    
    

    def stackbar(self, ntop=None, other='other', **kwargs):
        if ntop :
            top = self.top(ntop)
        else :
            top = self.order_cols()
        stacked = top.cumsum()
        stacked[other] = self.sum_rows()
        for cat in reversed(stacked.categories):
            stacked.move_to_end(cat)
        stacked.bar(stacked.time_column, **kwargs)
