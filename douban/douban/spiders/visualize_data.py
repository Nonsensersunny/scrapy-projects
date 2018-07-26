'''
import json
from collections import Counter
# print(dict(Counter("".join("This is an example string for couting each word in this phrase".split()))))


years = []
stars = []
evals = []
with open('./test.json', 'r') as data:
    data = data.read()
    jdata = json.loads(data)
    for item in jdata:
        years.append(int(item['year'][1:5]))
        stars.append(float(item['star']))
        evals.append(int(item['evaluate']))

# metaData = zip(years, stars, evals)
# pac = [list(i) for i in metaData]
# print(pac)


year_dict = dict(Counter(years))
star_dict = dict(Counter(stars))


import numpy as np
import matplotlib.pyplot as plt

# Year frequency plot
# plt.plot(year_dict.keys(), year_dict.values(), label='Frequency/Year')
# plt.legend()
# plt.show()

# Star frequency bar
plt.bar(star_dict.keys(), star_dict.values())
plt.show()

# 载入模块
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

# 创建 3D 图形对象
fig = plt.figure()
ax = Axes3D(fig)

# 生成数据并绘图
x = star_dict.keys()
for i in x:
    y = year_dict.values()
    z = abs(np.random.normal(1, 10, 10))
    ax.bar(y, z, i, zdir='y', color=['r', 'g', 'b', 'y'])
plt.show()

'''