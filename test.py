import jwt

secret = '2ed154d0c89362da0e2fc49257c5fb27c01cdfbc85238ea334e84dbc8eccfee3812b41add4149999b2277780b0edbdda4905f46f607fd3ffd8d3601113c1e7ae'

token = jwt.encode({'HELLO': 'WHAT IS UP'}, secret, algorithm='HS512')

print(token)

result = jwt.decode(token, secret, algorithms=['HS512'])
print(result)