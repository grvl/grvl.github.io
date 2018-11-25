"""latex_table_generator.py

Generates lines for a LaTeX table with the final results.
"""

from collections import defaultdict


ZN_DICT = {
    'Centro': 'Central',
    'Leste': 'East',
    'Oeste': 'West',
    'Norte': 'North',
    'Sul': 'South',
}


def print_table_line(obj):
    def fscore(score, pad=8):
        res = '-' if score is None else '%.04f' % score
        return res.ljust(pad)

    print u' & '.join([
        str(obj['scores']['total']['ranking']).ljust(3),
        u'{} ({})'.format(
            obj['name'].ljust(18),
            ZN_DICT[obj['zone']][:1]
        ),
        fscore(obj['scores']['venues']['value']),
        fscore(obj['scores']['topography']['value']),
        fscore(obj['scores']['bus']['value']),
        fscore(obj['scores']['parking']['value']),
        fscore(obj['scores']['subway']['value']),
        fscore(obj['scores']['total']['value']),
    ]) + '\\\\'


def get_zone_avgs(ds):
    def avg(arr):
        arr = filter(lambda num: num is not None, arr)
        return sum(arr) / len(arr)

    zones = defaultdict(list)     # Dict with zone name and district list.
    for d in ds:
        zones[d['zone']].append(d)

    for name, zds in zones.items():
        print u'{}: {} districts. {}\n'.format(name, len(zds),
            u', '.join(sorted(map(lambda d: d['name'], zds))))

    return [
        {
            'name': ZN_DICT[name],
            'zone': name,
            'scores': {
                score_name: {
                    'ranking': '-',     # Calculate manually, it's 5 zones.
                    'value': avg(
                        map(lambda d: d['scores'][score_name]['value'], zds))
                }
                for score_name in zds[0]['scores'].keys()
            }
        } for name, zds in zones.items()
    ]


def main():
    with open('../../js/data/distritos-ranked.json') as f:
        import json
        data = json.load(f)

    ds = sorted(
        map(lambda el: el['properties'], data['features']),
        key=lambda el: el['scores']['total']['ranking']
    )

    for d in ds:
        print_table_line(d)

    print '\n'
    for zn in get_zone_avgs(ds):
        print_table_line(zn)

if __name__ == '__main__':
    main()
