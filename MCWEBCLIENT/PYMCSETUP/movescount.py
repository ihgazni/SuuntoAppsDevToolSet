import navegador5 as nv 
import navegador5.url_tool as nvurl
import navegador5.head as nvhead
import navegador5.body as nvbody
import navegador5.cookie 
import navegador5.cookie.cookie as nvcookie
import navegador5.cookie.rfc6265 as nvrfc6265
import navegador5.jq as nvjq
import navegador5.js_random as nvjr
import navegador5.file_toolset as nvft
import navegador5.shell_cmd as nvsh
import navegador5.html_tool as nvhtml
import navegador5.solicitud as nvsoli
import navegador5.content_parser 
import navegador5.content_parser.amf0_decode as nvamf0
import navegador5.content_parser.amf3_decode as nvamf3

import lxml.html
from lxml import etree
import json
import re
import urllib.parse
import os
from PIL import Image


try:
    from xdict.jprint import pobj
except:
    print("you cant use some debug functions")
else:
    pass


def movescount_get_real_base_url(base_url):
    # when you use different ip ,the real base_url is different
    ##   for example, when you use in china, the real base_url is "http://www.movescount.cn/zh/" when you using 'http://www.movescount.com/'
    ##                when you use in jp, the real base_url is "http://www.movescount.com/" when you using 'http://www.movescount.com/'
    ##                or 
    ##                "http://www.movescount.com/zh/" when you using 'http://www.movescount.com/zh/'
    # when not use vpn: there will be many redirects:
    #1. base_url = "http://www.movescount.com/"
    ## ('Location', 'http://www.movescount.com/go?u=%2f&tld=cn&c=en')
    #2. base_url = "https://www.movescount.com/"
    ## ('Location', 'http://www.movescount.com/go?u=%2f&tld=cn&c=en')
    #3. base_url = "http://www.movescount.com/zh"
    ## ('Location', '/zh/')
    #4. base_url = "http://www.movescount.com/zh/"
    ## ('Location', 'http://www.movescount.com/go?u=%2fzh%2f&tld=cn&c=zh')
    #5. base_url = "https://www.movescount.com/zh"
    ## ('Location', '/zh/')
    #6. base_url = "https://www.movescount.com/zh/"
    ## ('Location', 'http://www.movescount.com/go?u=%2fzh%2f&tld=cn&c=zh')
    #  info_container['url'] = 'http://www.movescount.com/go?u=%2fzh%2f&tld=cn&c=zh'
    ## ('Location', 'http://www.movescount.cn/go?u=%2fzh%2f&tld=cn&c=zh&notldredir=true')
    #  info_container['url'] = 'http://www.movescount.cn/go?u=%2fzh%2f&tld=cn&c=zh&notldredir=true'
    ## ('Location', '/zh/')
    #  info_container['url'] = 'http://www.movescount.cn/zh/'
    ## 
    # when not use vpn(via jp): there will be many redirects:
    info_container = nvsoli.new_info_container()
    info_container['url'] = base_url
    info_container['method'] = 'GET'
    req_head_str = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.94 Safari/537.36\r\nAccept-Encoding: gzip,deflate,sdch\r\nAccept-Language: en;q=1.0, zh-CN;q=0.8'''
    info_container['req_head'] = nvhead.build_headers_dict_from_str(req_head_str,'\r\n')
    info_container['req_head']['Connection'] = 'close'
    #### init records_container
    records_container = nvsoli.new_records_container()
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    info_container = nvsoli.auto_redireced(info_container,records_container)
    return(info_container['url'])

def movescount_init_login(emailAddress,password):
    base_url = 'https://www.movescount.com/'
    base_url = movescount_get_real_base_url(base_url)
    info_container = nvsoli.new_info_container()
    info_container['base_url'] = base_url
    servicegate_url_dict = {
        'scheme':"https",
        'netloc':"servicegate.suunto.com",
        'path':"UserAuthorityService",
        'query_dict':{
            'callback': nvjq.jQuery_get_random_jsonpCallback_name(),
            'emailAddress':emailAddress,
            'password':password,
            '_':nvjq.jQuery_unix_now(),
            'service':"Movescount"
        }
    }
    info_container['url'] = nvurl.dict_to_url(servicegate_url_dict)
    info_container['method'] = 'GET'
    req_head_str = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.94 Safari/537.36\r\nAccept-Encoding: gzip,deflate,sdch\r\nAccept-Language: en;q=1.0, zh-CN;q=0.8'''
    info_container['req_head'] = nvhead.build_headers_dict_from_str(req_head_str,'\r\n')
    netloc = urllib.parse.urlparse(base_url).netloc
    referer_url = ''.join(("https://",netloc,"/auth?redirect_uri=%2foverview"))
    info_container['req_head']['Referer'] = referer_url
    info_container['req_head']['Connection'] = 'close'
    #### init records_container
    records_container = nvsoli.new_records_container()
    return((info_container,records_container,servicegate_url_dict))

def movescount_login(info_container,records_container,servicegate_url_dict):
    #step0:获取 token
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    resp_body_bytes = info_container['resp_body_bytes']
    token = nvjq.jQuery_get_jsonp_reply_arguments(resp_body_bytes,servicegate_url_dict['query_dict']['callback'])
    #step1: 存储获得到的登陆cookie:
    netloc = urllib.parse.urlparse(info_container['base_url']).netloc
    info_container['url'] = ''.join(("https://",netloc,"/services/UserAuthenticated"))
    #info_container['url'] = "https://www.movescount.com/services/UserAuthenticated"
    info_container['req_head']['Content-Type'] = 'application/json; charset=utf-8'
    info_container['method'] = 'POST'
    ##-----json body
    utcOffset = nvjq.jQuery_get_utcOffset()
    redirectUri = "/overview"
    req_body_dict = {
        'token':token,
        'utcOffset':utcOffset,
        'redirectUri':redirectUri
    }
    req_body = nvbody.handle_req_body_via_content_type(info_container['req_head']['Content-Type'],req_body_dict)
    info_container['req_body'] = req_body
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    return((info_container,records_container))

def movescount_get_windowSuuntoConfig(info_container,records_container):
    '''
        ####step 2 获取windowSuuntoConfig_dict
        info_container,records_container,windowSuuntoConfig_dict = movescount_get_windowSuuntoConfig(info_container,records_container)
    '''
    netloc = urllib.parse.urlparse(info_container['base_url']).netloc
    info_container['url'] = ''.join(("https://",netloc,"/overview"))
    info_container['method'] = 'GET'
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    # to solve a strange error  that the GET request include a Content-Length, resend the request will solve this
    error = nvhead.select_headers_via_key_from_tuple_list(info_container['resp_head'],'X-Squid-Error')
    if(error == []):
        pass
    else:
        info_container = nvsoli.walkon(info_container,records_container=records_container)
    resp_body_bytes = info_container['resp_body_bytes']
    #nvft.write_to_file(fn='overview.html',content=resp_body_bytes,op='wb+')
    html_text = resp_body_bytes.decode('utf-8')
    root = etree.HTML(html_text)
    selector = ''.join(('//script'))
    eles = root.xpath(selector)
    json_str = ''
    for i in range(0,eles.__len__()):
        if(eles[i].items().__len__() == 0):
            if("window.suunto.Config" in eles[i].text):
                regex = re.compile("window.suunto.Config[ ]*=[ ]*(\{.*\})[ \r\n]*;")
                m = regex.search(eles[i].text)
                json_str = m.group(1)
            else:
                pass
        else:
            pass
    windowSuuntoConfig_dict = json.loads(json_str)
    return((info_container,records_container,windowSuuntoConfig_dict))

def movescount_creat_app_search_params(selector,root):
    eles = root.xpath(selector)
    if(eles.__len__()>0):
        options = eles[0].getchildren()
    else:
        return({})
    rslt = {}
    for i in range(0,options.__len__()):
        rslt[options[i].get('value')]=options[i].text
        rslt[options[i].text]=options[i].get('value')
    return(rslt)

def movescount_format_loadcomponent_query_dict(loadcomponent_query_dict,options_ref_dict):
    for key in loadcomponent_query_dict:
        old_index = loadcomponent_query_dict[key]
        loadcomponent_query_dict[key] = str(old_index)
        if(key == 'sorting'):
            try:
                int(old_index)
            except:
                regex = re.compile('t([0-9]+)')
                m = regex.search(old_index)
                if(m):
                    t = m.group(1)
                    loadcomponent_query_dict['type'] = int(t)
                    loadcomponent_query_dict['sorting'] = 5
                else:
                    if(old_index in options_ref_dict['sorting']):  
                        loadcomponent_query_dict[key] = options_ref_dict['sorting'][loadcomponent_query_dict[key]]
                    else:
                        loadcomponent_query_dict[key] = 10
            else:
                if(old_index in options_ref_dict['sorting']):
                    pass
                else:
                    loadcomponent_query_dict[key] = 10
        if(key == 'activity'):
            if(old_index == ""):
                pass
            else:
                try:
                    int(old_index)
                except:
                    if(old_index in options_ref_dict['activity']):  
                        if(old_index =="Select"):
                            loadcomponent_query_dict[key] = ""
                        else:
                            loadcomponent_query_dict[key] = options_ref_dict['sorting'][loadcomponent_query_dict[key]]
                    else:
                        loadcomponent_query_dict[key] = ""
                else:
                    if(old_index in options_ref_dict['activity']):
                        if(old_index =="1"):
                            loadcomponent_query_dict[key] = ""
                        else:
                            pass
                    else:
                        loadcomponent_query_dict[key] = ""
        if(key == 'ruleCategory'):
            try:
                int(old_index)
            except:
                if(old_index in options_ref_dict['sorting']):
                    loadcomponent_query_dict[key] = options_ref_dict['ruleCategory'][loadcomponent_query_dict[key]]
                else:
                    loadcomponent_query_dict[key] = ""
            else:
                if(old_index in options_ref_dict['ruleCategory']):
                    pass
                else:
                    loadcomponent_query_dict[key] = ""
    return(loadcomponent_query_dict)

def movescount_get_loadcomponet_query_url(info_container,records_container,loadcomponent_query_params={},query_params={}):
    '''
        ####step 3 访问"http://www.movescount.com/apps" 获取loadcomponet_query_url
        #info_container,records_container,loadcomponet_query_url,root= mc.movescount_get_loadcomponet_query_url(info_container,records_container,loadcomponent_query_params={'sorting':5},query_params={})
    '''
    netloc = urllib.parse.urlparse(info_container['base_url']).netloc
    info_container['method'] = 'GET'
    info_container['url'] = ''.join(("http://",netloc,"/apps"))
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    charset = nvhead.get_content_type_from_resp(info_container['resp'])['charset']
    html_text = info_container['resp_body_bytes'].decode(charset)
    if(html_text == ''):
        html_text='<html><body></body></html>'
    else:
        pass
    root = etree.HTML(html_text)
    if(loadcomponent_query_params=={}):
        loadcomponent_query_dict = {
            'page':1,
            'sorting':10,
            'activity':"",
            'type':0,
            'term':"",
            'ruleCategory':""
        }
    else:
        loadcomponent_query_dict = {
            'page':1,
            'sorting':10,
            'activity':"",
            'type':0,
            'term':"",
            'ruleCategory':""
        }
        for key in loadcomponent_query_params:
            if(key in loadcomponent_query_dict):
                loadcomponent_query_dict[key] = loadcomponent_query_params[key]
    options_ref_dict = {}
    selector_ruleCategory = ''.join(('//select[@id=','"','ctl00_topArea_ListCategoryDdl','"]'))
    options_ref_dict['ruleCategory'] = movescount_creat_app_search_params(selector_ruleCategory,root)
    selector_sorting = ''.join(('//select[@id=','"','ListOrderDdl','"]'))
    options_ref_dict['sorting'] = movescount_creat_app_search_params(selector_sorting,root)
    selector_activity = ''.join(('//select[@id=','"','ctl00_topArea_ListActivityDdl','"]'))
    options_ref_dict['activity'] = movescount_creat_app_search_params(selector_activity,root)
    pobj(options_ref_dict)
    #http://www.movescount.com/loadcomponent?clientID=items&componentID=RuleItems&page=1&sorting=10&type=0&ruleCategory=2&_=1486223869668
    loadcomponent_query_dict = movescount_format_loadcomponent_query_dict(loadcomponent_query_dict,options_ref_dict)
    # for type ="t1" "t2" ......
    loadcomponent_query_dict = movescount_format_loadcomponent_query_dict(loadcomponent_query_dict,options_ref_dict)
    if(query_params=={}):
        query_template = {
            'clientID':"items",
            'componentID':"RuleItems",
            'page':"1",
            'sorting':"10",
            'activity':"",
            'type':"0",
            'term':"",
            'ruleCategory':"",
            '_':nvjq.jQuery_unix_now()
        }
    else:
        query_template = {
            'clientID':"items",
            'componentID':"RuleItems",
            'page':"1",
            'sorting':"10",
            'activity':"",
            'type':"0",
            'term':"",
            'ruleCategory':"",
            '_':nvjq.jQuery_unix_now()
        }
        for key in query_params:
            if(key in query_template):
                query_template[key] = query_params[key]
    for key in query_template:
        if(key in loadcomponent_query_dict):
            query_template[key] = loadcomponent_query_dict[key]
    query_dict = {}
    for key in query_template:
        if(query_template[key] == ""):
           pass
        else:
           query_dict[key] = query_template[key]
    query_url = nvurl.urlencode(query_dict)
    query_url = ''.join(("http://",netloc,"/loadcomponent?",query_url))
    #query_url = ''.join(("http://www.movescount.com/zh/loadcomponent?",query_url))
    #--------
    #--------
    return((info_container,records_container,query_url,root))

def movescount_get_my_apps_info(info_container,records_container):
    info_container,records_container,loadcomponet_query_url,root = movescount_get_loadcomponet_query_url(info_container,records_container,loadcomponent_query_params={'sorting':'My Apps'},query_params={})
    info_container['method'] = 'GET'
    info_container['url'] = loadcomponet_query_url
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    charset = nvhead.get_content_type_from_resp(info_container['resp'])['charset']    
    html_text = info_container['resp_body_bytes'].decode(charset)    
    if(html_text == ''):    
        html_text='<html><body></body></html>'    
    else:    
        pass
    root = etree.HTML(html_text)
    selector = ''.join(('//html/body/ul/li/div/div/a[@href and @class]'))
    eles = root.xpath(selector)
    netloc = urllib.parse.urlparse(info_container['base_url']).netloc
    info_container['method'] = 'GET'
    my_apps_info = []
    for i in range(0,eles.__len__()):
        href = eles[i].get('href')
        regex = re.compile('app([0-9]+)-(.*)')
        m = regex.search(eles[i].get('href'))
        RuleID = m.group(1)
        app_name = m.group(2)
        my_app_url = ''.join(("http://",netloc,href))
        info = {}
        info['url'] = my_app_url
        info['name'] = app_name
        info['RuleID'] = RuleID
        my_apps_info.append(info)
    pobj(my_apps_info)
    return((info_container,records_container,my_apps_info))


def movescount_get_loadcomponet_pages_num(info_container,records_container):
    info_container,records_container,loadcomponet_query_url,apps_root= movescount_get_loadcomponet_query_url(info_container,records_container)
    info_container['req_head']['Referer'] = info_container['url']
    info_container['method'] = 'GET'
    info_container['url'] = loadcomponet_query_url
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    charset = nvhead.get_content_type_from_resp(info_container['resp'])['charset']
    html_text = info_container['resp_body_bytes'].decode(charset)
    root = etree.HTML(html_text)
    selector = ''.join(('//input[','@id="items_paging"',' and ','@type="hidden"',']'))
    eles = root.xpath(selector)
    pages = eles[0].get('value').split('/')
    curr_page = pages[0]
    total_page = pages[1]
    return({'total':total_page,'current':curr_page,'apps_root':apps_root})

def movescount_get_all_loadcomponet_pages(info_container,records_container,start=1,end=-1,save=1):
    #pages_root_dict = movescount_get_all_loadcomponet_pages(info_container,records_container)
    apps_pages_info = movescount_get_loadcomponet_pages_num(info_container,records_container)
    total_page = apps_pages_info['total']
    relative_dir_path = 'loadcomponet'
    apps_root = apps_pages_info['apps_root']
    loadcomponent_query_dict = {
        'page':1,
        'sorting':10,
        'activity':"",
        'type':0,
        'term':"",
        'ruleCategory':""
    }
    if(save):
        if(os.path.exists(relative_dir_path)):
            pass
        else:
            os.mkdir(relative_dir_path)
    else:
        pass
    page_roots_dict = {}
    if(end>int(total_page)):
        end = int(total_page)
    elif(end<0):
        end = int(total_page)
    else:
        pass
    for i in range(start,int(end)+1):
        loadcomponent_query_dict['page'] = i
        info_container,records_container,url,root = movescount_get_loadcomponet_query_url(info_container,records_container,loadcomponent_query_params=loadcomponent_query_dict)
        print("---------------------------------------------------")
        print(url)
        print(info_container['resp_head'])
        print("---------------------------------------------------")
        info_container['url'] = url
        info_container['method'] = 'GET'
        info_container = nvsoli.walkon(info_container,records_container=records_container)
        charset = nvhead.get_content_type_from_resp(info_container['resp'])['charset']
        html_text = info_container['resp_body_bytes'].decode(charset)
        if(html_text == ''):
            html_text='<html><body></body></html>'
        else:
            pass
        try:
            page_roots_dict[i] = etree.HTML(html_text)
        except:
            print("---Exception etree.HTML(html_text)---------")
            print(info_container['resp_body_bytes'])
            print("---Exception etree.HTML(html_text)---------")
            print(html_text)
            page_roots_dict[i] = None
        else:
            pass
        if(save):
            regex = re.compile("/loadcomponent\?(.*)")
            fn_part = regex.search(url).groups(1)[0]
            nvft.write_to_file(fn=''.join(('./loadcomponet/','p',str(i),'.','html')),content=info_container['resp_body_bytes'],op='wb+')
            nvft.write_to_file(fn=''.join(('./loadcomponet/','p',str(i),'.','desc.txt')),content=''.join(('<!--\n',fn_part,'\n',loadcomponent_query_dict.__str__(),'\n-->')),op='w+')
        else:
            pass
    return(page_roots_dict)

def movescount_get_all_apps_description(base_url,page_roots_dict):
    #
    #apps_desc_dict =  movescount_get_all_apps_description(info_container['base_url'],page_roots_dict)
    apps_desc_dict = {}
    seq = 1
    for i in range(1,page_roots_dict.__len__()+1):
        selector_each_app = ''.join(('//html/body/ul/li/div'))
        root_each_app = page_roots_dict[i]
        eles_each_app = root_each_app.xpath(selector_each_app)
        for j in range(0,eles_each_app.__len__()):
            app = {}
            ele = eles_each_app[j]
            app['data-id'] = ele.get('data-id')
            selector = ''.join(('./div/a'))
            app['app-url'] = ''.join((base_url,ele.xpath(selector)[0].get('href')))
            selector = ''.join(('./div/div/img'))
            app['icon-url'] = ''.join(('http',ele.xpath(selector)[0].get('src')))
            selector = ''.join(('./div/div/ul/li/div'))
            app['class-text'] = ele.xpath(selector)[0].text
            selector = ''.join(('./div/div/ul/li/div/div/h5/a'))
            app['app-title'] = ele.xpath(selector)[0].get('title')
            app['app-text'] = ele.xpath(selector)[0].text
            selector = ''.join(('./div/div/ul/li/div/a'))
            app['member-url'] = ''.join((base_url,ele.xpath(selector)[0].get('href')))
            app['member-title'] = ele.xpath(selector)[0].get('title')
            app['member-text'] = ele.xpath(selector)[0].text
            selector = ''.join(('./div/div/ul/li/div/a/following-sibling::*'))
            approvals_number = ele.xpath(selector)[0].text
            regex = re.compile('[0-9]+')
            m = regex.search(approvals_number)
            if(m):
                app['approvals-number'] = int(m.group(0))
            else:
                app['approvals-number'] = 0
            selector = ''.join(('./div/div/ul/li/div/div/div/p'))
            if(ele.xpath(selector).__len__()==0):
                app['description'] = ""
            else:
                app['description'] = ele.xpath(selector)[0].text
            apps_desc_dict[seq] = app
            seq = seq + 1
    return(apps_desc_dict)


def get_app_creat_root(info_container,records_container):
    #info_container,records_container,app_creat_root = get_app_creat_root(info_container,records_container)
    info_container['method'] = 'GET'
    netloc = urllib.parse.urlparse(info_container['base_url']).netloc
    info_container['url'] = ''.join(("http://",netloc,"/apps/app"))
    info_container['req_head']['Upgrade-Insecure-Requests'] = 1
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    charset = nvhead.get_content_type_from_resp(info_container['resp'])['charset']
    html_text = info_container['resp_body_bytes'].decode(charset)    
    if(html_text == ''):
        html_text='<html><body></body></html>'
    else:
        pass
    app_creat_root = etree.HTML(html_text)
    info_container['Referer'] = info_container['url']
    info_container['Cache-Control'] = 'no-cache'
    return((info_container,records_container,app_creat_root))


def movescount_get_aspnetForm_input_dict(root):
    #aspnetForm_input_dict = movescount_get_aspnetForm_input_dict(app_creat_root)
    eles = root.xpath('//input[@type!="text"]')
    aspnetForm_input_dict = {}
    for i in range(0,eles.__len__()):
        if(eles[i].get('value') == None):
            value = ''
        else:
            value = eles[i].get('value')
        aspnetForm_input_dict[eles[i].get('name')] = value
    return(aspnetForm_input_dict)

def movescount_get_aspnetForm_text_dict(root):
    #aspnetForm_text_dict = movescount_get_aspnetForm_text_dict(app_creat_root)
    aspnetForm_text_dict = {}
    eles = root.xpath('//input[@type="text"]')
    for i in range(0,eles.__len__()):
        if(eles[i].get('value') == None):
            value = ''
        else:
            value = eles[i].get('value')
        aspnetForm_text_dict[eles[i].get('name')] = value
    eles = root.xpath('//textarea')
    for i in range(0,eles.__len__()):
        if(eles[i].get('value') == None):
            value = ''
        else:
            value = eles[i].get('value')
        aspnetForm_text_dict[eles[i].get('name')] = value
    return(aspnetForm_text_dict)

def movescount_get_aspnetForm_selects(root):
    #aspnetForm_selects = movescount_get_aspnetForm_selects(app_creat_root)
    aspnetForm_select_dict = {}
    eles = root.xpath('//select')
    aspnetForm_PublicityDropDownList = {}
    aspnetForm_ActivityDropDownList = {}
    aspnetForm_CategoryDropDownList = {}    
    aspnetForm_language_select_dict = {}
    for i in range(0,eles.__len__()):
        if(eles[i].get('value') == None):
            value = ''
        else:
            value = eles[i].get('value')
        name = eles[i].get('name')
        if(name):
            aspnetForm_select_dict[name] = value
            regex = re.compile("(.*)\$(.*)")
            m = regex.search(name)
            if(m):
                name = m.group(2)
            else:
                pass
            if(name == "PublicityDropDownList"):
                aspnetForm_PublicityDropDownList = movescount_creat_app_search_params('.',eles[i])
            if(name == "ActivityDropDownList"):
                aspnetForm_ActivityDropDownList = movescount_creat_app_search_params('.',eles[i])
            if(name == "CategoryDropDownList"):
                aspnetForm_CategoryDropDownList = movescount_creat_app_search_params('.',eles[i])
        else:
            aspnetForm_language_select_dict = movescount_creat_app_search_params('.',eles[i])
    return({'select':aspnetForm_select_dict,
            'options':{'publicity':aspnetForm_PublicityDropDownList,
                       'activity':aspnetForm_ActivityDropDownList,
                       'category':aspnetForm_CategoryDropDownList}})

def movescount_creat_ct100_query_dict_template(aspnetForm_input_dict,aspnetForm_selects,Activity='',Category = ''):
    #ct100_query_dict = movescount_creat_ct100_query_dict_template(aspnetForm_input_dict,aspnetForm_selects)
    ct100_query_dict = {}
    DescriptionText = ''
    RuleNameText = ''
    TagsText = ''
    WebsiteText = ''
    masterPageUniqueID = 'ctl00'
    scriptManagerID = 'ctl00$MainScriptManager'
    panelsToUpdate = 'ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$UploadFromWeb'
    asyncTarget = 'ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$ImportBrowseButton'
    updatePanelIDs = [
    'ctl00$fullWidthPageContent$ctl00$ctl00$RuleImageUpdatePanel',
    'ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$RootUpdatePanel',
    'ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$CropUpdatePanel',
    'ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$UploadFromWeb',
    'ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$UpdatePanel1',
    'ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$CancelButtonUpdatePanel',
    'ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$CropButtonUpdatePanel'
    ]
    aspnetForm_ActivityDropDownList = aspnetForm_selects['options']['activity']
    if(not (Activity in aspnetForm_ActivityDropDownList)):
        Activity = 'Select'
    aspnetForm_CategoryDropDownList = aspnetForm_selects['options']['category']
    if(not (Category in aspnetForm_CategoryDropDownList)):
        Category = 'Training'
    ct100_query_dict[scriptManagerID] = "ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$UploadFromWeb|ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$ImportBrowseButton"
    ct100_query_dict['ctl00$topArea$ActivityDropDownList'] = str(aspnetForm_ActivityDropDownList[Activity])
    ct100_query_dict['ctl00$topArea$PublicityDropDownList'] =  'false'  
    ct100_query_dict['ctl00$topArea$CategoryDropDownList'] =  str(aspnetForm_CategoryDropDownList[Category])
    ct100_query_dict['ctl00$topArea$DescriptionTextBox']  = DescriptionText
    ct100_query_dict['ctl00$topArea$RuleNameTextBox']  = RuleNameText      
    ct100_query_dict['ctl00$topArea$TagsTextBox'] =  TagsText    
    ct100_query_dict['ctl00$topArea$WebsiteTextBox'] = WebsiteText
    ct100_query_dict['__EVENTTARGET'] = aspnetForm_input_dict['__EVENTTARGET']
    ct100_query_dict['__EVENTARGUMENT'] = aspnetForm_input_dict['__EVENTARGUMENT']
    ct100_query_dict['__VIEWSTATE'] = aspnetForm_input_dict['__VIEWSTATE']
    ct100_query_dict['__VIEWSTATEGENERATOR'] = aspnetForm_input_dict['__VIEWSTATEGENERATOR']
    ct100_query_dict['__EVENTVALIDATION'] = aspnetForm_input_dict['__EVENTVALIDATION']
    ct100_query_dict['ctl00$fullWidthPageContent$ctl00$ctl00$RuleImageHf'] = aspnetForm_input_dict['ctl00$fullWidthPageContent$ctl00$ctl00$RuleImageHf']
    ct100_query_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$VisibilityHf'] = aspnetForm_input_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$VisibilityHf']
    ct100_query_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$LinkTextBox'] = aspnetForm_input_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$LinkTextBoxButton']
    ct100_query_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$HiddenImageName'] = aspnetForm_input_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$HiddenImageName']
    ct100_query_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$CroppedImageNameField'] = aspnetForm_input_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$CroppedImageNameField']
    ct100_query_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$X'] = aspnetForm_input_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$X']
    ct100_query_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$Y'] = aspnetForm_input_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$Y']
    ct100_query_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$W'] = aspnetForm_input_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$W']
    ct100_query_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$H'] = aspnetForm_input_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$H']
    ct100_query_dict['__ASYNCPOST'] = 'true'
    ct100_query_dict[''] = ''
    return(ct100_query_dict)


def movescount_crop_icon_image(src_img_name,x=0,y=0,w=61,h=45):
    dst_img_name = ''.join(('cropped_',src_img_name))
    img = Image.open(src_img_name)
    img = img.crop( (x,y,w,h) )
    #img.thumbnail([200, 200], Image.ANTIALIAS)
    file_destination=dst_img_name
    imagefile = open(file_destination, 'wb')
    try:
        img.save(imagefile, "png", quality=90)
        imagefile.close()
    except:
        return()
    else:
        pass
    return(dst_img_name)

def movescount_get_temp_uploaded_img_url(info_container,records_container,icon_img_name = 'test_icon.png'):
    # info_container,records_container,temp_img_url = movescount_get_temp_uploaded_img_url(info_container,records_container,icon_img_name)
    info_container['req_head']['Referer'] = info_container['url']
    info_container['req_head']['Cache-Control'] = 'no-cache'
    netloc = urllib.parse.urlparse(info_container['base_url']).netloc
    info_container['url'] = ''.join(("http://",netloc,"/ImageHandler.ashx"))
    boundary = ''.join(('--',nvjq.jQuery_unix_now(14)))
    multitipary_header_dict = {
        0: ('', 'multipart/form-data'), 
        1: ('boundary', boundary), 
        'name': 'Content-Type'
    }
    info_container['req_head']['Content-Type'] = nvhead.encode_one_http_head(multitipary_header_dict,'Content-Type','; ')
    dispositions = {}
    dispositions[0] = {
        'headers': {
            0: {
                0: ('', 'form-data'), 
                1: ('name', '"Filedata"'),
                2: ('filename', '"test_logo.png"'), 
                'name': 'Content-Disposition'
            }, 
            1: {
                0: ('', 'image/png'),
                'name': 'Content-Type'
            }
        }, 
        'body': nvft.read_file_content(fn=icon_img_name,op='rb').decode('latin')
    }
    multipart_text = nvbody.encode_multipart_dict(boundary,dispositions,multitipary_header_dict,with_multitipary_header=0)
    multipart_bin = bytes(multipart_text,'latin')
    info_container['method'] = 'POST'
    info_container['req_body'] = multipart_bin
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    charset = nvhead.get_content_type_from_resp(info_container['resp'])['charset']
    temp_img_url = ''.join(('http:',info_container['resp_body_bytes'].decode(charset)))
    return((info_container,records_container,temp_img_url))

def movescount_creat_icon_crop_dict(ct100_query_dict,kwargs_dict):
    #ct100_query_dict = 
    #上传修改后的image参数 X Y W H
    scriptManagerID = 'ctl00$MainScriptManager'
    ct100_query_dict[scriptManagerID] = "ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$CropButtonUpdatePanel|ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$CropButton"
    ct100_query_dict['__EVENTTARGET'] = "ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$CropButton"
    #crop 图片
    ct100_query_dict['ctl00$fullWidthPageContent$ctl00$ctl00$RuleImageHf'] = 'True'
    ct100_query_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$VisibilityHf'] = ''
    ct100_query_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$LinkTextBox'] = ''
    ct100_query_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$HiddenImageName'] = kwargs_dict['tempImageURL']
    ## 上一步上传的图片的url
    ct100_query_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$CroppedImageNameField'] = ''
    ct100_query_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$X'] = kwargs_dict['X']
    ct100_query_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$Y'] = kwargs_dict['Y']
    ct100_query_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$W'] = kwargs_dict['W']
    ct100_query_dict['ctl00$fullWidthPageContent$ctl00$ctl00$PictureSlicer1$H'] = kwargs_dict['H']
    #
    ct100_query_dict['ctl00$topArea$DescriptionTextBox']  = kwargs_dict['DescriptionText']
    ct100_query_dict['ctl00$topArea$RuleNameTextBox']  = kwargs_dict['RuleNameText']      
    ct100_query_dict['ctl00$topArea$TagsTextBox'] =  kwargs_dict['TagsText']    
    ct100_query_dict['ctl00$topArea$WebsiteTextBox'] = kwargs_dict['WebsiteText']
    return(ct100_query_dict)


def movescount_creat_save_dict_template_dict_file(name=str(nvjq.jQuery_random_number()),fn='save_dict_template.js'):
    s1 = '{\n "rule": \n         {\n          "CategoryID": 0, \n          "RuleID": 0, \n          "Description": "------DESCRIPTION----", \n          "Tags": \n                  [\n                   "----TAGS---"\n                  ], \n          "Source": "/* While in sport mode do this once per second */\\nRESULT = SUUNTO_SWIMMING_POOL_LENGTH;", \n          "ActivityID": 6, \n          "Name": "'
    s2 = '", \n          "Prefix": "PRE", \n          "OutputFormatID": 1, \n          "Postfix": "POS", \n          "WebSiteURL": "http://www.dapeli.com", \n          "UserVariables": \n                           [\n                            {\n                             "Name": "OWNVAR1", \n                             "Value": 0\n                            }, \n                            {\n                             "Name": "OWNVAR2", \n                             "Value": 200\n                            }\n                           ], \n          "SourceTree": null, \n          "SimulationValues": \n                              [\n                               {\n                                "Name": "SUUNTO_SWIMMING_POOL_LENGTH", \n                                "Value": 100\n                               }\n                              ]\n         }\n}\n'
    s = s1 + name + s2 
    nvft.write_to_file(fn=fn,op='w',content=s)

def movescount_get_save_dict_template_params_from_file(name=str(nvjq.jQuery_random_number()),fn='save_dict_template.js'):
    fp = open(fn,'r')
    save_dict_template_params = json.loads(fp.read(),strict=False)
    save_dict_template_params['Name'] = name 
    return(save_dict_template_params)

def movescount_get_creat_app_body_query_str(info_container,records_container,icon_img_name,icon_crop_kwargs_params={},save_dict_template_params={}):
    info_container,records_container,app_creat_root = get_app_creat_root(info_container,records_container)
    aspnetForm_input_dict = movescount_get_aspnetForm_input_dict(app_creat_root)
    aspnetForm_text_dict = movescount_get_aspnetForm_text_dict(app_creat_root)
    aspnetForm_seclects = movescount_get_aspnetForm_selects(app_creat_root)
    ct100_query_dict = movescount_creat_ct100_query_dict_template(aspnetForm_input_dict,aspnetForm_seclects)
    icon_crop_kwargs = {
        'Activity' : '',
        'Category' : '',
        'DescriptionText' : '',
        'RuleNameText' : '',
        'TagsText' : '',
        'WebsiteText' : '',
        'tempImageURL': '',
        'X':0,
        'Y':0,
        'W':61,
        'H':45
    }
    for key in icon_crop_kwargs_params:
        if(key in icon_crop_kwargs):
            icon_crop_kwargs[key] = icon_crop_kwargs_params[key]
    dst_img_name = movescount_crop_icon_image(icon_img_name,icon_crop_kwargs['X'],icon_crop_kwargs['Y'],icon_crop_kwargs['W'],icon_crop_kwargs['H'])
    info_container,records_container,temp_img_url = movescount_get_temp_uploaded_img_url(info_container,records_container,dst_img_name)
    icon_crop_kwargs['tempImageURL'] = temp_img_url
    ct100_query_dict = movescount_creat_icon_crop_dict(ct100_query_dict,icon_crop_kwargs)
    info_container['req_head']['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'
    info_container['method'] = 'POST'
    info_container['req_body'] = nvurl.urlencode(ct100_query_dict)
    netloc = urllib.parse.urlparse(info_container['base_url']).netloc
    info_container['url'] = ''.join(("http://",netloc,"/apps/app"))
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    charset = nvhead.get_content_type_from_resp(info_container['resp'])['charset']
    html_text = info_container['resp_body_bytes'].decode(charset)    
    if(html_text == ''):
        html_text='<html><body></body></html>'
    else:
        pass
    root = etree.HTML(html_text)
    eles = root.xpath('//div/img[@class="upload-img"]')
    RuleImage_url_post_crop = ''.join(('http',eles[0].get('src')))
    eles = root.xpath('//div/input[@id="ctl00_fullWidthPageContent_ctl00_ctl00_RuleImageHf"]')
    RuleImageHf_relative_url_post_crop = eles[0].get('value')
    save_dict_template = {
        "rule": {
            "OutputFormatID": 1,
            "Postfix": "POS",
            "Prefix": "PRE",
            "SourceTree": None,
            #None will be transed to null by json
            "Source": "/* While in sport mode do this once per second */\nRESULT = SUUNTO_SWIMMING_POOL_LENGTH;",
            "UserVariables": [{
                "Name": "OWNVAR1",
                "Value": 0
            }, {
                "Name": "OWNVAR2",
                "Value": 200
            }],
            "SimulationValues": [{
                "Name": "SUUNTO_SWIMMING_POOL_LENGTH",
                "Value": 100
            }],
            "RuleID": 0,
            "ImageURL": RuleImageHf_relative_url_post_crop,
            "Name": "TEST-UPLOAD-",
            "ActivityID": 6,
            "IsPublic": False,
            #False will be transed to false by json
            "CategoryID": 0,
            "Description": "------DESCRIPTION----",
            "Tags": ["----TAGS---"],
            "WebSiteURL": "http://www.dapeli.com"
        }
    }
    for key in save_dict_template_params:
        if(key in save_dict_template):
            save_dict_template[key] = save_dict_template_params[key]
    save_query_string = json.dumps(save_dict_template)
    verify_dict_template = {
        "rule": {
            "OutputFormatID": save_dict_template['rule']['OutputFormatID'],
            "Postfix": save_dict_template['rule']['Postfix'],
            "Prefix": save_dict_template['rule']['Prefix'],
            "SourceTree": save_dict_template['rule']['SourceTree'],
            "Source": save_dict_template['rule']['Source'],
            "UserVariables": save_dict_template['rule']['UserVariables'],
            "SimulationValues": save_dict_template['rule']['SimulationValues'],
            "Name": save_dict_template['rule']['Name']
        }
    }
    verify_query_string = json.dumps(verify_dict_template)
    return((info_container,records_container,save_query_string,verify_query_string))

    
def movescount_verify(info_container,records_container,verify_query_string):
    netloc = urllib.parse.urlparse(info_container['base_url']).netloc
    info_container['url'] = ''.join(("http://",netloc,"/services/RuleDesignerVerifyRule"))
    info_container['method'] = 'POST'
    info_container['req_head']['Content-Type'] = 'application/json; charset=utf-8'
    info_container['req_head']['Accept'] = 'application/json, text/javascript, */*; q=0.01'
    info_container['req_head']['X-Requested-With'] = 'XMLHttpRequest'
    info_container['req_body'] = verify_query_string
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    charset = nvhead.get_content_type_from_resp(info_container['resp'])['charset']
    html_text = info_container['resp_body_bytes'].decode(charset)
    verify_rslt_dict = json.loads(html_text)
    pobj(verify_rslt_dict)
    return(verify_rslt_dict)


def movescount_save(info_container,records_container,save_query_string):
    netloc = urllib.parse.urlparse(info_container['base_url']).netloc
    info_container['url'] = ''.join(("http://",netloc,"/services/RuleDesignerSaveRule"))
    info_container['req_head']['Content-Type'] = 'application/json; charset=utf-8'
    info_container['req_head']['Accept'] = 'application/json, text/javascript, */*; q=0.01'
    info_container['req_head']['X-Requested-With'] = 'XMLHttpRequest'
    info_container['method'] = 'POST'
    info_container['req_body'] = save_query_string
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    charset = nvhead.get_content_type_from_resp(info_container['resp'])['charset']
    html_text = info_container['resp_body_bytes'].decode(charset)
    save_rslt_dict = json.loads(html_text)
    Name = str(save_rslt_dict['d']['Value']['RuleInfo']['Rule']['Name'])
    RuleID = str(save_rslt_dict['d']['Value']['RuleInfo']['Rule']['RuleID'])
    app_url = ''.join((info_container['base_url'],'apps/app',RuleID,'-',Name))
    pobj(save_rslt_dict)
    return((info_container,records_container,app_url,RuleID,save_rslt_dict))

#
def movecount_remove(info_container,records_container,app_url,RuleID):
    remove_query_string = json.dumps({"ruleId":RuleID})
    netloc = urllib.parse.urlparse(info_container['base_url']).netloc
    info_container['url'] = ''.join(("http://",netloc,"/services/RemoveRule"))
    info_container['req_head']['Content-Type'] = 'application/json; charset=utf-8'
    info_container['req_head']['Accept'] = 'application/json, text/javascript, */*; q=0.01'
    info_container['req_head']['X-Requested-With'] = 'XMLHttpRequest'
    info_container['req_head']['Referer'] = app_url
    info_container['method'] = 'POST'
    info_container['req_body'] = remove_query_string
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    charset = nvhead.get_content_type_from_resp(info_container['resp'])['charset']
    html_text = info_container['resp_body_bytes'].decode(charset)
    remove_rslt_dict = json.loads(html_text)
    pobj(remove_rslt_dict)
    return(remove_rslt_dict)
    
def movecount_pull_save_template_dict(info_container,records_container,app_url):
    #save_template_dict_for_edit,full_info_for_edit = movecount_pull_save_template_dict(info_container,records_container,app_url)
    info_container['url'] = app_url
    info_container['method'] = 'GET'
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    charset = nvhead.get_content_type_from_resp(info_container['resp'])['charset']    
    html_text = info_container['resp_body_bytes'].decode(charset)
    if(html_text == ''):
        html_text='<html><body></body></html>'
    else:
        pass
    root = etree.HTML(html_text)
    eles = root.xpath('//form/script')
    script = eles[-1].text
    regex = re.compile('mc.RulePage.default.main\((.*)\)')
    m = regex.search(script)
    js = m.group(1)
    d = json.loads(js,strict=False)
    return((d['rule'],d))
    
def movecount_edit(info_container,records_container,app_url,save_template_dict_for_edit,save_dict_template_params={}):
    #save_template_dict_for_edit,full_info_for_edit = movecount_pull_save_template_dict(info_container,records_container,app_url)
    #pobj(save_template_dict_for_edit)
    #save_dict_template_params = 
    #movecount_edit(info_container,records_container,app_url,save_template_dict_for_edit,save_dict_template_params)
    for key in save_dict_template_params:
        if(key in save_template_dict_for_edit):
            save_template_dict_for_edit[key] = save_dict_template_params[key]
    save_query_string = json.dumps(save_template_dict_for_edit)
    rslt = movescount_save(info_container,records_container,save_query_string)
    return(rslt)


# ---------------------------------------------------- 

