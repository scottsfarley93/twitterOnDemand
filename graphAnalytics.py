__author__ = 'scottsfarley'
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

analytics = {'topHashtags': [(u'Syria', 144), (u'iacaucus', 57), (u'Trump2016', 46), (u'voteja2016', 44), (u'ISIS', 40)], 'currentRate': 1.9, 'timestamp': '2016-01-31 20:31:27.278693', 'topTimezones': [(None, 728), (u'Eastern Time (US & Canada)', 266), (u'Pacific Time (US & Canada)', 207), (u'Central Time (US & Canada)', 204), (u'Quito', 47)], 'topURLS': [(u'http://bbc.in/1JT66wD', 56), (u'http://bbc.in/1KQDgro', 34), (u'https://twitter.com/hughhewitt/status/693910409535954945', 16), (u'http://www.alraimedia.com/ar/article/special-reports/2016/02/01/653787/nr/syria', 14), (u'https://twitter.com/davidplouffe/status/693929588590669824', 14)], 'numTweets': 1923, 'executionTime': 0.007778085283411331, 'topUsers': [(u'SHAJU05', 8), (u'azadar087', 7), (u'newnews4all', 7), (u'EjmAlrai', 6), (u'IvanSidorenko1', 6)], 'topLanguages': [(u'en', 1789), (u'und', 62), (u'no', 10), (u'in', 10), (u'fr', 9)], 'topLocations': [(None, 625), (u'Jamaica', 77), (u'United States', 26), (u'Kingston, Jamaica', 17), (u'USA', 15)], 'avgRate': 1.7613352907975373, 'topMentions': [(u'JaredWyand', 47), (u'BBCWorld', 34), (u'BernieSanders', 22), (u'emilymshields', 22), (u'LizSly', 19)], 'topPlatforms': [(u'<a href="http://twitter.com/download/android" rel="nofollow">Twitter for Android</a>', 439), (u'<a href="http://twitter.com/download/iphone" rel="nofollow">Twitter for iPhone</a>', 429), (u'<a href="http://twitter.com" rel="nofollow">Twitter Web Client</a>', 401), (u'<a href="http://twitterfeed.com" rel="nofollow">twitterfeed</a>', 140), (u'<a href="http://twitter.com/#!/download/ipad" rel="nofollow">Twitter for iPad</a>', 78)]}

import plotly
import plotly.offline
print plotly.__version__  # version >1.9.4 required
plotly.offline.init_notebook_mode()
from plotly.graph_objs import Scatter, Layout
plotly.offline.iplot({
"data": [
    Scatter(x=[1, 2, 3, 4], y=[4, 1, 3, 7])
],
"layout": Layout(
    title="hello world"
)
})