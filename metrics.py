import datetime
import time
from datadog import initialize, api
from decouple import config
from texttable import Texttable

options = {
    'api_key': config('API_KEY'),
    'app_key': config('APP_KEY')
}

initialize(**options)


def list_metrics(seconds_back=60 * 60 * 24 * 7):
    from_time = int(time.time()) - seconds_back
    result = api.Metric.list(from_time)
    metrics = result['metrics']
    # print(len(metrics), 'Total')
    metrics = [x for x in metrics if 'buildhub' in x.lower()]
    print(len(metrics), 'Buildhubs')
    for i, metric in enumerate(metrics):
        print(i + 1, repr(metric))


def _get_series(query, seconds_back=60 * 60 * 24):
    now = int(time.time())
    result = api.Metric.query(start=now - seconds_back, end=now, query=query)
    if not result.get('series'):
        print(result)
        raise Exception('No series found')
    return result['series']


def show_time_series(key, limit=10):
    query = 'buildhub.' + key + '.avg{*}by{env}'
    series = _get_series(query, 60 * 60 * 24 * 7)

    print()
    print((f'  {key.upper()}  ').center(80, '='))
    print()
    for serie in series:
        print(f"SCOPE: {serie['scope'].upper()}")
        table = Texttable()
        # table.set_cols_align(["l", "r", "c"])
        # table.set_cols_valign(["t", "m", "b"])
        rows = [['WHEN', 'TIME AGO', 'TIME TOOK']]
        for ts, seconds in list(reversed(serie['pointlist']))[:limit]:
            if not seconds:
                # XXX strange that there are those that are None
                continue
            then = datetime.datetime.utcfromtimestamp(ts / 1000)
            rows.append([
                then.strftime('%a') + ' ' + then.isoformat(),
                humanize_seconds(
                    (datetime.datetime.utcnow() - then).total_seconds()
                ) + ' ago',
                humanize_seconds(seconds / 1000)
            ])
        table.add_rows(rows)
        print(table.draw())
        print('\n')


def _humanize_time(amount, units):
    """Chopped and changed from http://stackoverflow.com/a/6574789/205832"""
    intervals = (1, 60, 60 * 60, 60 * 60 * 24, 604800, 2419200, 29030400)
    names = (
        ("second", "seconds"),
        ("minute", "minutes"),
        ("hour", "hours"),
        ("day", "days"),
        ("week", "weeks"),
        ("month", "months"),
        ("year", "years"),
    )

    result = []
    unit = [x[1] for x in names].index(units)
    # Convert to seconds
    amount = amount * intervals[unit]
    for i in range(len(names) - 1, -1, -1):
        a = int(amount) // intervals[i]
        if a > 0:
            result.append((a, names[i][1 % a]))
            amount -= a * intervals[i]
    return result


def humanize_seconds(seconds, units=2):
    parts = _humanize_time(seconds, "seconds")[:units]
    return ' '.join("{} {}".format(*x) for x in parts)


def show_metric(metric):
    print(api.Metadata.get(metric_name=metric))


if __name__ == '__main__':
    # list_metrics()

    show_time_series('to_kinto_fetch_existing')
    show_time_series('s3_inventory_to_kinto_run')
