import requests, json


headers = {
    'X-RapidAPI-Key': '2789440bc9mshdbfa4cc80af7ff7p16bcf9jsn61795c27b039',
    'X-RapidAPI-Host': 'seeking-alpha.p.rapidapi.com'
}

link = 'symbols/get-summary'
response = requests.get('https://seeking-alpha.p.rapidapi.com/symbols/get-summary', headers=headers, params={'symbols': 'abbv'})
with open('res_abbv_2.txt', 'w', encoding='utf-8') as file:
    file.write('============== ' + link + ' ==============\n')
    if not 'data' in json.loads(response.text):
        file.write(response.text)
    else:
        for one in json.loads(response.text)['data'][0]:
            try:
                try:
                    for two in json.loads(response.text)['data'][0][one]:
                        file.write(str(two) + ': ' + str(json.loads(response.text)['data'][0][one][two]) + '\n')
                except Exception as e:
                    file.write(str(one) + ': ' + str(json.loads(response.text)['data'][0][one]) + '\n')
            except:
                file.write(str(one) + '\n')
    file.write('\n\n')

exit()

main_part = 'https://seeking-alpha.p.rapidapi.com/'
links = ['market/get-equity',
'market/get-market-open',
'market/get-day-watch',
'market/get-realtime-prices',
'market/get-dividend-investing',

'symbols/get-meta-data',
'symbols/get-profile',
'symbols/get-summary',
'symbols/get-peers',
'symbols/get-dividend-history',
'symbols/v2/get-momentum',
'symbols/get-valuation',
'symbols/get-metrics',
'symbols/get-key-data',
'symbols/get-fundamentals',
'symbols/get-chart',
'symbols/v2/get-chart',
'symbols/get-estimates',
'symbols/get-holdings',
'symbols/get-top-holdings',
'symbols/get-earnings',
'symbols/get-factor-grades',
'symbols/get-quant-rating-histories',
'symbols/get-analyst-ratings',
'symbols/get-analyst-price-target',
'symbols/get-analyst-recommendations',
'symbols/get-momentum',
'symbols/get-ratings',

'analysis/v2/list',
'analysis/v2/get-details',
'analysis/get-details',
'analysis/list',

'articles/v2/list',
'articles/v2/list-trending',
'articles/list-wall-street-breakfast',
'articles/get-details',
'articles/list',
'articles/list-trending',

'news/v2/list',
'news/v2/list-by-symbol',
'news/v2/list-trending',
'news/list',
'news/list-trending',
'news/get-details',

'press-releases/v2/list',
'press-releases/get-details',
'press-releases/list',

'transcripts/v2/list',
'transcripts/v2/get-details',
'transcripts/get-details',
'transcripts/list',

'comments/list',
'comments/v2/list',
'comments/get-contents',
'comments/get-sub-comments',

'screeners/list',
'screener-filters/list',
'screeners/detail']


for cmp_name in ['aapl', 'abbv']:
    data = {
        'market/get-equity': {'filterCategory': 'global-equity'},
        'market/get-market-open': None,
        'market/get-day-watch': None,
        'market/get-realtime-prices': {'symbols': f'{cmp_name}'},
        'market/get-dividend-investing': None,

        'symbols/get-meta-data': {'symbol': f'{cmp_name}'},
        'symbols/get-profile': {'symbols': f'{cmp_name}'},
        'symbols/get-summary': {'symbols': f'{cmp_name}'},
        'symbols/get-peers': {'symbol': f'{cmp_name}'},
        'symbols/get-dividend-history': {'symbol': f'{cmp_name}', 'years': '6', 'group_by': 'year'},
        'symbols/v2/get-momentum': {'symbols': f'{cmp_name}', 'fields': 'chgp3m,chgp6m,chgp9m,chgp1y,low52,high52'},
        'symbols/get-valuation': {'symbols': f'{cmp_name}'},
        'symbols/get-metrics': {
                    'symbols': 'ipoof,tga,esea,bgfv,grin,bbw',
                    'fields': 'quant_rating,authors_rating_pro,sell_side_rating,marketcap,dividend_yield,value_category,growth_category,profitability_category,momentum_category,eps_revisions_category'
                },
        'symbols/get-key-data': {'symbol': f'{cmp_name}'},
        'symbols/get-fundamentals': {'symbol': f'{cmp_name}', 'limit': '4', 'period_type': 'annual'},
        'symbols/get-chart': {'symbol': f'{cmp_name}', 'period': '1Y'},
        'symbols/v2/get-chart': {
                'symbols': f'{cmp_name}',
                'start': '2021-06-25',
                'end': '2022-07-06',
                'metrics': 'total_revenue'
            },
        'symbols/get-estimates': {'symbol': f'{cmp_name}', 'data_type': 'revenues', 'period_type': 'quarterly'},
        'symbols/get-holdings': {'symbols': f'{cmp_name}'},
        'symbols/get-top-holdings': {'symbol': f'{cmp_name}'},
        'symbols/get-earnings': {
                'ticker_ids': '1742,146',
                'period_type': 'quarterly',
                'relative_periods': '-3,-2,-1,0,1,2,3',
                'estimates_data_items': 'eps_gaap_actual,eps_gaap_consensus_mean,eps_normalized_actual,eps_normalized_consensus_mean,revenue_actual,revenue_consensus_mean',
                'revisions_data_items': 'eps_normalized_actual,eps_normalized_consensus_mean,revenue_consensus_mean'
            },
        'symbols/get-factor-grades': {'symbols': f'{cmp_name}'},
        'symbols/get-quant-rating-histories': {'symbol': f'{cmp_name}', 'number': '1'},
        'symbols/get-analyst-ratings': {'symbol': f'{cmp_name}'},
        'symbols/get-analyst-price-target': {'ticker_ids': '146', 'return_window': '1', 'group_by_month': 'false'},
        'symbols/get-analyst-recommendations': {'ticker_ids': '146', 'return_window': '3', 'group_by_month': 'true'},
        'symbols/get-momentum': {'symbols': f'{cmp_name}'},
        'symbols/get-ratings': {'symbol': f'{cmp_name}'},

        'analysis/v2/list': {'id': f'{cmp_name}', 'until': '0', 'since': '0', 'size': '20', 'number': '1'},
        'analysis/v2/get-details': {'id': '4341786'},
        'analysis/get-details': {'id': '4341786'},
        'analysis/list': {'id': f'{cmp_name}', 'until': '0', 'size': '20'},

        'articles/v2/list': {'until': '0', 'since': '0', 'size': '20', 'number': '1', 'category': 'latest-articles'},
        'articles/v2/list-trending': {'until': '0', 'since': '0', 'size': '20'},
        'articles/list-wall-street-breakfast': None,
        'articles/get-details': {'id': '4349447'},
        'articles/list': {'category': 'latest-articles', 'until': '0', 'size': '20'},
        'articles/list-trending': None,

        'news/v2/list': {'category': 'market-news::all', 'until': '0', 'since': '0', 'size': '20', 'number': '1'},
        'news/v2/list-by-symbol': {'id': f'{cmp_name}', 'until': '0', 'since': '0', 'size': '20', 'number': '1'},
        'news/v2/list-trending': {'until': '0', 'since': '0', 'size': '20'},
        'news/list': {'id': f'{cmp_name}', 'until': '0', 'size': '20'},
        'news/list-trending': None,
        'news/get-details': {'id': '3577036'},

        'press-releases/v2/list': {'id': f'{cmp_name}', 'until': '0', 'since': '0', 'size': '20', 'number': '1'},
        'press-releases/get-details': {'id': '17867968'},
        'press-releases/list': {'id': f'{cmp_name}', 'until': '0', 'size': '20'},

        'transcripts/v2/list': {'id': f'{cmp_name}', 'until': '0', 'since': '0', 'size': '20', 'number': '1'},
        'transcripts/v2/get-details': {'id': '4341792'},
        'transcripts/get-details': {'id': '4341792'},
        'transcripts/list': {'id': 'aapl', 'until': '0', 'size': '20'},

        'comments/list': {'id': '4405526', 'from_id': '88004158', 'parent_count': '20', 'sort': '-top_parent_id'},
        'comments/v2/list': {'id': '4469484', 'sort': '-top_parent_id'},
        'comments/get-contents': {'id': '4469484', 'comment_ids': '90666350', 'sort': '-top_parent_id'},
        'comments/get-sub-comments': {'id': '90949998', 'sort': '-top_parent_id'},

        'screeners/list': None,
        'screener-filters/list': None,
        'screeners/detail': {'id': '96793299'}
    }
    with open(f'res_{cmp_name}.txt', 'w') as file:
        for link in links:
            url = main_part + link

            if data[link] is None:
                response = requests.get(url, headers=headers)
            else:
                response = requests.get(url, headers=headers, params=data[link])
            
            if response.status_code != 200:
                print(link + f' - status_code = {response.status_code}')
                continue

            try:
                file.write('============== ' + link + ' ==============\n')
                if not 'data' in json.loads(response.text):
                    file.write(response.text)
                else:
                    for one in json.loads(response.text)['data']:
                        try:
                            file.write(str(one) + ': ' + str(json.loads(response.text)['data'][one]) + '\n')
                        except:
                            file.write(str(one) + '\n')
                file.write('\n\n')
            except:
                print(link + ' - FAILED')
                continue

            print(link)