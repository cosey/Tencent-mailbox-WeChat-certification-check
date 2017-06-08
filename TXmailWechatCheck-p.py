# coding: utf-8

import  requests
import  json
import  smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

def gettoken(CorpID,CorpSecret ):
    url = "https://api.exmail.qq.com/cgi-bin/gettoken?corpid=" + CorpID + "&corpsecret=" + CorpSecret
    r1 = requests.get(url)
    r2 = json.loads(r1.content)
    if r2.has_key("access_token"):
        token=r2["access_token"]
        #print token
        return token
    else:
        print "error-token"
        exit(0)

'''
def getdepartment(token,id):
    requrl = "https://api.exmail.qq.com/cgi-bin/department/list?access_token=" + token + "&id=" + id
    r1 = requests.get(requrl)
    r2 = json.loads(r1.text)
    if r2["errmsg"] == "ok":
        #for x in r2["department"]:
            if id==x["id"]:
                return x["name"]
            else:
                return "null"
    else:
        print "error-id"
        exit(0)
'''

def getid(token,DEPARTMENT_ID,FETCH_CHILD):
    requrl = "https://api.exmail.qq.com/cgi-bin/user/simplelist?access_token="+token+"&department_id="+DEPARTMENT_ID+"&fetch_child="+FETCH_CHILD
    r1 = requests.get(requrl)
    r2 = json.loads(r1.text)
    if r2["errmsg"]=="ok":
        return r2["userlist"]
    else:
        print "error-id"
        exit(0)

def judgeid(ACCESS_TOKEN,USERID):
    i=0
    for x in USERID:
        url = "https://api.exmail.qq.com/cgi-bin/user/get?access_token=" + ACCESS_TOKEN + "&userid=" + x["userid"]
        r1 = requests.get(url)
        r2 = json.loads(r1.text)
        if r2["enable"] == 0:
            USERID.pop(i)
        i=i+1
    return USERID

def checkservice(token,id):
    requrl = "https://api.exmail.qq.com/cgi-bin/useroption/get?access_token=" + token
    unopen = []
    for x in id:
        test_data = {
            "userid": x["userid"],
            "type":[1,2,3,4]
        }
        req = requests.post(requrl , json =test_data)
        req2 = json.loads(req.content)
        #department=getdepartment(token,x['department'])
        #print x['department']
        if  req2["errmsg"]=="ok" :
            #if req2["option"][3]['value'] == "1":
               #print x["name"].encode('utf8')+"微信动态码启用,账号为"+x["userid"].encode('utf8')#+",所属部门为"+department
            if req2["option"][3]['value'] == "0":
                print x["name"].encode('utf8')+"微信动态码未开启,账号为"+x["userid"].encode('utf8')#+",所属部门为"+department
                unopen.append(x)
        else:
            print "error-service"
            exit(0)
    return unopen

def mail(sender,password,senderid,receiver):
    for x in receiver:
        try:
            msg=MIMEText('您的腾讯企业邮箱未开启微信二次认证，请及时开启！','plain','utf-8')
            msg['From'] = formataddr(["腾讯企业邮箱微信二次认证检测脚本", sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To'] = formataddr([x["name"], x["userid"]])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = "微信二次认证检测警告"

            server = smtplib.SMTP("smtp.163.com", 25)  # 发件人邮箱中的SMTP服务器，端口是25
            server.login(sender, password)  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(sender, [x["userid"], ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()
        except Exception:
            print "发送邮件给" + x["userid"].encode('utf-8')+ "失败"
            exit(0)
        print "发送邮件给"+x['userid'].encode('utf-8')+"成功"


if __name__ == '__main__':

    CorpID="CorpID"
    CorpSecret="CorpSecret"
    CorpSecret_connect="CorpSecret_connect"

    token=gettoken(CorpID,CorpSecret)
    token_c=gettoken(CorpID,CorpSecret_connect)

    #id=raw_input()    
    #department= "0"
    #id=getdepartment(token_c,department)

    DEPARTMENT_ID = "1"
        #获取的部门id。id为1时可获取根部门下的成员
    FETCH_CHILD = "1"
        #1/0：是否递归获取子部门下面的成员
    id=getid(token_c,DEPARTMENT_ID,FETCH_CHILD)
    updateId=judgeid(token_c, id)
    unopenId=checkservice(token,updateId)

    sender="sender"
    password="password"
    senderid="senderid"
    receiver=unopenId
    mail(sender, password, senderid, receiver)


