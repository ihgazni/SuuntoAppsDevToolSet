import sys
sys.path.append('../PYMCSETUP/')
from movescount import *

if(__name__ == "__main__"):
    emailAddress = sys.argv[2]
    password = sys.argv[4]
    info_container,records_container,servicegate_url_dict = movescount_init_login(emailAddress,password)
    info_container,records_container = movescount_login(info_container,records_container,servicegate_url_dict)
    action = sys.argv[6]
    if(action == 'remove'):
        app_url = sys.argv[8]
        RuleID  = sys.argv[10]
        movecount_remove(info_container,records_container,app_url,RuleID)
    elif(action == 'save'):
        icon_img_name = sys.argv[8]
        app_name = sys.argv[10]
        file_name = sys.argv[12]
        save_dict_template_params = movescount_get_save_dict_template_params_from_file(app_name,file_name)
        info_container,records_container,save_query_string,verify_query_string =  movescount_get_creat_app_body_query_str(info_container,records_container,icon_img_name,{},save_dict_template_params)
        info_container,records_container,app_url,RuleID,save_rslt_dict = movescount_save(info_container,records_container,save_query_string)
    elif(action == 'myapps'):
        info_container,records_container, my_apps_info= movescount_get_my_apps_info(info_container,records_container)
    else:
        pass

#python3 apps.py -user "......@163.com" -passwd "......" -action myapps | tee myapps.log

#python3 apps.py -user "......@163.com" -passwd "......" -action remove -app_url "http://www.movescount.cn/zh/apps/app11662421-TEST-UPLOAD-" -RuleID "11662421" | tee remove.log

#python3 apps.py -user "......@163.com" -passwd "......" -action save -icon_image test_icon.png  -app_name "go......test" -file_name "save_dict_template.js" | tee save.log

