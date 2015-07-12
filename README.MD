##这是一个使用tornado构建的IM服务器实例

* 简单的用户登入，登出
* 全用户广播通知、用户对用户点对点聊天

## 准备工作

* tornado
* requests
* futures

## How to use?
使用命令启动服务
```bash
python serv.py #start service

```
####登陆:使用浏览器访问http://localhost:8888/user/byname/Billy/login (其中Billy是用户名)返回值是包括uid。
####发起websocket:使用浏览器调用ws接口，如下
```javascript
var s = new WebSocket('ws://localhost:8888/user/byid/1')  //1为uid
s.onmessage = function(v){console.log(v.data)}
s.send('{"to_uid":"1","content":"hello!"}') //to_uid 为对方uid，登陆多个用户之后使用
```


##有问题反馈
在使用中有任何问题，欢迎反馈给我，可以用以下联系方式跟我交流

* 邮件(rowland.lan@163.com)
* QQ: 623135465
* weibo: [@都说名字长点帅](http://weibo.com/u/2461323585)


##关于作者

```javascript
  var ihubo = {
    nickName  : "nikoloss",
    site : "http://www.zhihu.com/people/luo-ran-22"
  }
```