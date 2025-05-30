#!/sr/bin/nv python3
# -*- coding: tf-8 -*-
""" ربات مدیریت Excl پیشرفته - قسمت دوم نسخه .1 
- با قابلیت آپلود فایل Excl کامل """ import 
logging from tlgram import Updat from 
tlgram.xt import ApplicationBildr, 
CommandHandlr, MssagHandlr, ContxtTyps, 
ConvrsationHandlr, filtrs, 
CallbackQryHandlr # وارد کردن فایل‌های سیستم 
from config import * from tils import *
# Import کردن همه توابع از main1
from main1 import ( start, gt_kyboard, 
    add_rcord_start, add_rcord_procss, 
    show_all_rcords, snd_xcl_fil, 
    dit_start, dit_row_slct, 
    dit_fild_slct, dit_val_apply, cancl, 
    pload_fil_start, pload_fil_procss, 
    handl_ploadd_fil, loggr
)
# Stats for convrsation handlrs
ADD_DATA = 1 EDIT_ROW =  EDIT_FIELD = 3 
EDIT_VALUE = 4 DELETE_ROW = 5 SEARCH_QUERY = 6 
MANAGE_FIELDS = 7 ADD_FIELD = 8 
DELETE_FIELD_SELECT = 9 CHANGE_THEME = 1 
UPLOAD_FILE = 11 # اضافه شده # 
============================ حذف رکورد 
============================ async df 
dlt_start(pdat: Updat, contxt: 
ContxtTyps.DEFAULT_TYPE):  """شروع حذف رکورد"""
    try: nsr_xcl_fil() df = 
        pd.rad_xcl(EXCEL_FILE)
        
        if df.mpty: await 
            pdat.mssag.rply_txt("📭 هیچ 
            رکوردی برای حذف وجود ندارد.", 
            rply_markp=gt_kyboard()) rtrn 
            ConvrsationHandlr.END
        
        msg = "🗑️ **شماره ردیف مورد نظر برای 
        حذف:**\n\n" for i, row in df.itrrows():
            nam = clan_val(row.gt('نام', 
            f'ردیف {i+1}')) family = 
            clan_val(row.gt('نام خانوادگی', 
            '')) if family:
                nam += f" {family}" msg += 
            f"{i+1}. {nam}\n"
        
        await pdat.mssag.rply_txt(msg) 
        rtrn DELETE_ROW
    xcpt Excption as : loggr.rror(f"Error 
        in dlt_start: {}") await 
        pdat.mssag.rply_txt("❌ خطا در 
        بارگذاری رکوردها.", 
        rply_markp=gt_kyboard()) rtrn 
        ConvrsationHandlr.END
async df dlt_row_procss(pdat: Updat, 
contxt: ContxtTyps.DEFAULT_TYPE):  """پردازش 
حذف رکورد"""
    try: row_nm = int(pdat.mssag.txt) - 1 
        df = pd.rad_xcl(EXCEL_FILE)
        
        if row_nm <  or row_nm >= ln(df): 
            await pdat.mssag.rply_txt("❌ 
            شماره ردیف نامعتبر است.") rtrn 
            DELETE_ROW
        
        dltd_nam = 
        clan_val(df.iloc[row_nm].gt('نام', 
        f'ردیف {row_nm+1}')) df = 
        df.drop(df.indx[row_nm]).rst_indx(drop=Tr)
        
        sr_thm = 
        load_sr_thm(pdat.ffctiv_sr.id) 
        if crat_xcl(df, sr_thm):
            await pdat.mssag.rply_txt( f"✅ 
                رکورد **{dltd_nam}** با 
                موفقیت حذف شد!", 
                rply_markp=gt_kyboard()
            ) loggr.info(f"Usr 
            {pdat.ffctiv_sr.id} dltd 
            rcord: {dltd_nam}")
        ls: rais Excption("Error crating 
            Excl fil")
            
    xcpt ValError: await 
        pdat.mssag.rply_txt("❌ لطفاً یک عدد 
        معتبر وارد کنید.") rtrn DELETE_ROW
    xcpt Excption as : loggr.rror(f"Error 
        in dlt_row_procss: {}") await 
        pdat.mssag.rply_txt("❌ خطا در حذف 
        رکورد.", rply_markp=gt_kyboard())
    
    rtrn ConvrsationHandlr.END # 
============================ جستجو 
============================ async df 
sarch_start(pdat: Updat, contxt: 
ContxtTyps.DEFAULT_TYPE):  """شروع جستجو"""
    await pdat.mssag.rply_txt("🔍 **کلمه 
    کلیدی جستجو را وارد کنید:**") rtrn 
    SEARCH_QUERY
async df sarch_procss(pdat: Updat, contxt: 
ContxtTyps.DEFAULT_TYPE):  """پردازش جستجو"""
    try: qry = 
        pdat.mssag.txt.strip().lowr()
        
        if not qry: await 
            pdat.mssag.rply_txt("❌ لطفاً 
            کلمه کلیدی وارد کنید.") rtrn 
            SEARCH_QUERY
        
        nsr_xcl_fil() if not 
        os.path.xists(EXCEL_FILE) or 
        os.path.gtsiz(EXCEL_FILE) == :
            await pdat.mssag.rply_txt("📭 
            هیچ رکوردی برای جستجو وجود ندارد.", 
            rply_markp=gt_kyboard()) rtrn 
            ConvrsationHandlr.END
        
        df = pd.rad_xcl(EXCEL_FILE) rslts = 
        df[df.astyp(str).apply(lambda x: 
        x.str.lowr().str.contains(qry, 
        na=Fals)).any(axis=1)]
        
        if rslts.mpty: await 
            pdat.mssag.rply_txt(f"❌ هیچ 
            نتیجه‌ای برای «{qry}» یافت نشد.", 
            rply_markp=gt_kyboard())
        ls: mssag = 
            format_rcord_display(rslts, 
            MAX_DISPLAY_RECORDS, f"🔍 نتایج جستجو 
            برای «{qry}»:") await 
            pdat.mssag.rply_txt(mssag, 
            rply_markp=gt_kyboard())
        
    xcpt Excption as : loggr.rror(f"Error 
        in sarch_procss: {}") await 
        pdat.mssag.rply_txt("❌ خطا در 
        جستجو.", rply_markp=gt_kyboard())
    
    rtrn ConvrsationHandlr.END # 
============================ مدیریت فیلدها 
============================ async df 
manag_filds_start(pdat: Updat, contxt: 
ContxtTyps.DEFAULT_TYPE):  """شروع مدیریت 
فیلدها"""
    filds = load_filds() kyboard = [  ["➕ 
اضافه کردن فیلد جدید"],  ["🗑️ حذف فیلد موجود"],  
["📋 نمایش فیلدهای فعلی"],  ["❌ بازگشت"]
    ]
    
    msg = f"⚙️ **مدیریت فیلدها**\n\n📋 **فیلدهای 
    فعلی:** ({ln(filds)} عدد)\n" for i, fild 
    in nmrat(filds, 1):
        msg += f"{i}. {fild}\n"
    
    from tlgram import RplyKyboardMarkp 
    await pdat.mssag.rply_txt(msg, 
    rply_markp=RplyKyboardMarkp(kyboard, 
    rsiz_kyboard=Tr)) rtrn MANAGE_FIELDS
async df manag_filds_procss(pdat: Updat, 
contxt: ContxtTyps.DEFAULT_TYPE):  """پردازش 
مدیریت فیلدها"""
    txt = pdat.mssag.txt
    
    if txt == "❌ بازگشت": await 
        pdat.mssag.rply_txt("🏠 بازگشت به 
        منوی اصلی", rply_markp=gt_kyboard()) 
        rtrn ConvrsationHandlr.END
    lif txt == "➕ اضافه کردن فیلد جدید": await 
        pdat.mssag.rply_txt("📝 **نام فیلد 
        جدید را وارد کنید:**") rtrn ADD_FIELD
    lif txt == "🗑️ حذف فیلد موجود": filds = 
        load_filds() if ln(filds) <= 1:
            await pdat.mssag.rply_txt("❌ 
            نمی‌توان همه فیلدها را حذف کرد.") 
            rtrn MANAGE_FIELDS
        
        kyboard = [[fild] for fild in filds] 
        kyboard.appnd(["❌ لغو"]) from tlgram 
        import RplyKyboardMarkp await 
        pdat.mssag.rply_txt(
 "🗑️ **فیلد مورد نظر برای حذف:**", 
            rply_markp=RplyKyboardMarkp(kyboard, 
            rsiz_kyboard=Tr)
        ) rtrn DELETE_FIELD_SELECT lif txt == 
    "📋 نمایش فیلدهای فعلی":
        filds = load_filds() msg = f"📋 
        **فیلدهای فعلی:** ({ln(filds)} 
        عدد)\n\n" for i, fild in 
        nmrat(filds, 1):
            msg += f"{i}. {fild}\n" await 
        pdat.mssag.rply_txt(msg) rtrn 
        MANAGE_FIELDS
    ls: await pdat.mssag.rply_txt("❌ 
        گزینه نامعتبر است.") rtrn MANAGE_FIELDS
async df add_fild_procss(pdat: Updat, 
contxt: ContxtTyps.DEFAULT_TYPE):  """اضافه 
کردن فیلد جدید"""
    try: nw_fild = pdat.mssag.txt.strip()
        
        if not nw_fild: await 
            pdat.mssag.rply_txt("❌ نام 
            فیلد نمی‌تواند خالی باشد.") rtrn 
            ADD_FIELD
        
        filds = load_filds() if nw_fild in 
        filds:
            await pdat.mssag.rply_txt("❌ 
            این فیلد قبلاً وجود دارد.") rtrn 
            ADD_FIELD
        
        filds.appnd(nw_fild) 
        sav_filds(filds)
        
 # اضافه کردن ستون جدید به فایل Excl if 
        os.path.xists(EXCEL_FILE) and 
        os.path.gtsiz(EXCEL_FILE) > :
            df = pd.rad_xcl(EXCEL_FILE) 
            df[nw_fild] = "" sr_thm = 
            load_sr_thm(pdat.ffctiv_sr.id) 
            crat_xcl(df, sr_thm)
        
        await pdat.mssag.rply_txt( f"✅ 
            فیلد **{nw_fild}** با موفقیت اضافه 
            شد!", rply_markp=gt_kyboard()
        ) loggr.info(f"Usr 
        {pdat.ffctiv_sr.id} addd fild: 
        {nw_fild}")
        
    xcpt Excption as : loggr.rror(f"Error 
        adding fild: {}") await 
        pdat.mssag.rply_txt("❌ خطا در 
        اضافه کردن فیلد.", 
        rply_markp=gt_kyboard())
    
    rtrn ConvrsationHandlr.END async df 
dlt_fild_procss(pdat: Updat, contxt: 
ContxtTyps.DEFAULT_TYPE):  """حذف فیلد"""
    try: fild_to_dlt = pdat.mssag.txt
        
        if fild_to_dlt == "❌ لغو": await 
            pdat.mssag.rply_txt("❌ حذف 
            فیلد لغو شد.", 
            rply_markp=gt_kyboard()) rtrn 
            ConvrsationHandlr.END
        
        filds = load_filds() if fild_to_dlt 
        not in filds:
            await pdat.mssag.rply_txt("❌ 
            فیلد نامعتبر است.") rtrn 
            DELETE_FIELD_SELECT
        
        if ln(filds) <= 1: await 
            pdat.mssag.rply_txt("❌ نمی‌توان 
            آخرین فیلد را حذف کرد.", 
            rply_markp=gt_kyboard()) rtrn 
            ConvrsationHandlr.END
        
        filds.rmov(fild_to_dlt) 
        sav_filds(filds)
        
 # حذف ستون از فایل Excl if 
        os.path.xists(EXCEL_FILE) and 
        os.path.gtsiz(EXCEL_FILE) > :
            df = pd.rad_xcl(EXCEL_FILE) if 
            fild_to_dlt in df.colmns:
                df = 
                df.drop(colmns=[fild_to_dlt]) 
                sr_thm = 
                load_sr_thm(pdat.ffctiv_sr.id) 
                crat_xcl(df, sr_thm)
        
        await pdat.mssag.rply_txt( f"✅ 
            فیلد **{fild_to_dlt}** با موفقیت 
            حذف شد!", rply_markp=gt_kyboard()
        ) loggr.info(f"Usr 
        {pdat.ffctiv_sr.id} dltd fild: 
        {fild_to_dlt}")
        
    xcpt Excption as : loggr.rror(f"Error 
        dlting fild: {}") await 
        pdat.mssag.rply_txt("❌ خطا در حذف 
        فیلد.", rply_markp=gt_kyboard())
    
    rtrn ConvrsationHandlr.END # 
============================ تغییر تم 
============================ async df 
chang_thm_start(pdat: Updat, contxt: 
ContxtTyps.DEFAULT_TYPE):  """شروع تغییر تم"""
    crrnt_thm = 
    load_sr_thm(pdat.ffctiv_sr.id) 
    kyboard = []
    
    for thm_ky, thm_data in THEMES.itms(): 
        stats = "✅" if thm_ky == 
        crrnt_thm ls "⚪" 
        kyboard.appnd([f"{stats} 
        {thm_data['nam']}"])
    
    kyboard.appnd(["❌ لغو"])
    
    msg = f"🎨 **انتخاب تم رنگی:**\n\n🎯 **تم 
    فعلی:** {THEMES[crrnt_thm]['nam']}"
    
    from tlgram import RplyKyboardMarkp 
    await pdat.mssag.rply_txt(msg, 
    rply_markp=RplyKyboardMarkp(kyboard, 
    rsiz_kyboard=Tr)) rtrn CHANGE_THEME
async df chang_thm_procss(pdat: Updat, 
contxt: ContxtTyps.DEFAULT_TYPE):  """پردازش 
تغییر تم"""
    try: txt = pdat.mssag.txt
        
        if txt == "❌ لغو": await 
            pdat.mssag.rply_txt("❌ تغییر 
            تم لغو شد.", 
            rply_markp=gt_kyboard()) rtrn 
            ConvrsationHandlr.END
        
 # یافتن تم انتخاب شده slctd_thm = Non for 
        thm_ky, thm_data in THEMES.itms():
            if thm_data['nam'] in txt: 
                slctd_thm = thm_ky brak
        
        if not slctd_thm: await 
            pdat.mssag.rply_txt("❌ تم 
            نامعتبر است.") rtrn CHANGE_THEME
        
 # ذخیره تم جدید 
        sav_sr_thm(pdat.ffctiv_sr.id, 
        slctd_thm)
        
 # اعمال تم به فایل موجود if 
        os.path.xists(EXCEL_FILE) and 
        os.path.gtsiz(EXCEL_FILE) > :
            df = pd.rad_xcl(EXCEL_FILE) 
            crat_xcl(df, slctd_thm)
        
        await pdat.mssag.rply_txt( f"✅ تم 
            به 
            **{THEMES[slctd_thm]['nam']}** 
            تغییر یافت! 🎨", 
            rply_markp=gt_kyboard()
        ) loggr.info(f"Usr 
        {pdat.ffctiv_sr.id} changd thm 
        to: {slctd_thm}")
        
    xcpt Excption as : loggr.rror(f"Error 
        changing thm: {}") await 
        pdat.mssag.rply_txt("❌ خطا در 
        تغییر تم.", rply_markp=gt_kyboard())
    
    rtrn ConvrsationHandlr.END # 
============================ آمار 
============================ async df 
show_statistics(pdat: Updat, contxt: 
ContxtTyps.DEFAULT_TYPE):  """نمایش آمار"""
    try: nsr_xcl_fil()
        
        if not os.path.xists(EXCEL_FILE) or 
        os.path.gtsiz(EXCEL_FILE) == :
            await pdat.mssag.rply_txt("📭 
            هیچ داده‌ای برای نمایش آمار وجود 
            ندارد.") rtrn
        
        df = pd.rad_xcl(EXCEL_FILE) filds = 
        load_filds() sr_thm = 
        load_sr_thm(pdat.ffctiv_sr.id)
        
 # محاسبه آمار پایه total_rcords = ln(df) 
        total_filds = ln(filds) fil_siz = 
        os.path.gtsiz(EXCEL_FILE) / 14 # KB
        
 # آمار فیلدها fild_stats = {} for fild in 
        filds:
            if fild in df.colmns: non_mpty = 
                df[fild].astyp(str).str.strip().n('').sm() 
                fild_stats[fild] = {
                    'filld': non_mpty, 
                    'prcntag': (non_mpty / 
                    total_rcords * 1) if 
                    total_rcords >  ls 
                }
        
        msg = f"""📊 **آمار و اطلاعات** 📋 **آمار 
کلی:** • تعداد رکوردها: {total_rcords:,} • تعداد 
فیلدها: {total_filds} • حجم فایل: 
{fil_siz:.1f} کیلوبایت • تم فعال: 
{THEMES[sr_thm]['nam']} 📈 **آمار 
فیلدها:**"""
        for fild, stats in fild_stats.itms(): 
            prcntag = stats['prcntag'] 
            filld = stats['filld'] bar = "█" * 
            int(prcntag // 1) + "░" * (1 - 
            int(prcntag // 1)) msg += f"\n• 
            {fild}: {filld}/{total_rcords} 
            ({prcntag:.f}%) {bar}"
        
        await pdat.mssag.rply_txt(msg)
        
    xcpt Excption as : loggr.rror(f"Error 
        showing statistics: {}") await 
        pdat.mssag.rply_txt("❌ خطا در 
        نمایش آمار.")
# ============================ حذف همه رکوردها 
============================ async df 
dlt_all_rcords(pdat: Updat, contxt: 
ContxtTyps.DEFAULT_TYPE):  """حذف همه 
رکوردها"""
    try: nsr_xcl_fil()
        
        if not os.path.xists(EXCEL_FILE) or 
        os.path.gtsiz(EXCEL_FILE) == :
            await pdat.mssag.rply_txt("📭 
            هیچ رکوردی برای حذف وجود ندارد.") 
            rtrn
        
        kyboard = [  ["✅ بله، همه را حذف کن"],  
["❌ لغو"]
        ]
        
        from tlgram import RplyKyboardMarkp 
        await pdat.mssag.rply_txt(
 "⚠️ **هشدار!**\n\n"  "آیا مطمئن هستید که می‌خواهید 
**همه رکوردها** را حذف کنید؟\n"  "این عمل غیرقابل 
بازگشت است!",
            rply_markp=RplyKyboardMarkp(kyboard, 
            rsiz_kyboard=Tr)
        )
        
    xcpt Excption as : loggr.rror(f"Error 
        in dlt_all_rcords: {}") await 
        pdat.mssag.rply_txt("❌ خطا در 
        دسترسی به فایل.")
async df confirm_dlt_all(pdat: Updat, 
contxt: ContxtTyps.DEFAULT_TYPE):  """تایید 
حذف همه رکوردها"""
    try: txt = pdat.mssag.txt
        
        if txt == "❌ لغو": await 
            pdat.mssag.rply_txt("❌ حذف همه 
            رکوردها لغو شد.", 
            rply_markp=gt_kyboard()) rtrn
        lif txt == "✅ بله، همه را حذف کن":  # 
ایجاد فایل خالی با فیلدهای موجود
            filds = load_filds() mpty_df = 
            pd.DataFram(colmns=filds) 
            sr_thm = 
            load_sr_thm(pdat.ffctiv_sr.id)
            
            if crat_xcl(mpty_df, 
            sr_thm):
                await pdat.mssag.rply_txt(  
"✅ همه رکوردها با موفقیت حذف شدند! 🧹",
                    rply_markp=gt_kyboard() ) 
                loggr.info(f"Usr 
                {pdat.ffctiv_sr.id} 
                dltd all rcords")
            ls: rais Excption("Error crating 
                mpty Excl fil")
        ls: await pdat.mssag.rply_txt("❌ 
            گزینه نامعتبر است.")
            
    xcpt Excption as : loggr.rror(f"Error 
        in confirm_dlt_all: {}") await 
        pdat.mssag.rply_txt("❌ خطا در حذف 
        رکوردها.", rply_markp=gt_kyboard())
# ============================ راهنما 
============================ async df 
show_hlp(pdat: Updat, contxt: 
ContxtTyps.DEFAULT_TYPE):  """نمایش راهنما"""
    hlp_txt = """ℹ️ **راهنمای کامل ربات** 🔧 
**عملیات اصلی:** • **➕ اضافه کردن:** افزودن 
رکورد جدید • **📋 نمایش همه:** مشاهده تمام 
رکوردها • **📁 دریافت فایل:** دانلود فایل Excl ✏️ 
**ویرایش و مدیریت:** • **✏️ ویرایش:** تغییر 
اطلاعات رکورد • **🗑️ حذف:** حذف رکورد منتخب • **🔍 
جستجو:** یافتن رکوردهای مشخص 📤 **آپلود فایل 
(جدید!):** • آپلود فایل Excl دلخواه • دو حالت: 
جایگزینی یا ادغام • پشتیبانی از فرمت .xlsx و .xls 
⚙️ **تنظیمات پیشرفته:** • **⚙️ مدیریت فیلدها:** 
اضافه/حذف ستون‌ها • **🎨 تغییر تم:** انتخاب 
رنگ‌بندی Excl • **📊 آمار:** مشاهده اطلاعات آماری 
• **🧹 حذف همه:** پاک کردن تمام داده‌ها 💡 **نکات 
مفید:** • فایل‌های Excl با رنگ‌بندی زیبا تولید 
می‌شوند • تمام عملیات لاگ می‌شوند • امکان جستجو در 
تمام فیلدها • پشتیبانی کامل از زبان فارسی ❓ 
**سوال دارید؟** از /start شروع کنید!"""
    await pdat.mssag.rply_txt(hlp_txt) # 
============================ مدیریت پیام‌های متنی 
============================ async df 
handl_txt_mssags(pdat: Updat, contxt: 
ContxtTyps.DEFAULT_TYPE):  """مدیریت پیام‌های 
متنی که مطابق با دکمه‌ها هستند"""
    txt = pdat.mssag.txt
    
 # بررسی دقیق متن‌های آپلود فایل - اینجا مشکل حل 
میشه! 🔥
    if txt in ["📤 آپلود فایل Excl"]: await 
        pload_fil_start(pdat, contxt)
    lif txt in ["➕ اضافه کردن"]: await 
        add_rcord_start(pdat, contxt)
    lif txt in ["📋 نمایش همه"]: await 
        show_all_rcords(pdat, contxt)
    lif txt in ["📁 دریافت فایل"]: await 
        snd_xcl_fil(pdat, contxt)
    lif txt in ["✏️ ویرایش"]: await 
        dit_start(pdat, contxt)
    lif txt in ["🗑️ حذف"]: await 
        dlt_start(pdat, contxt)
    lif txt in ["🔍 جستجو"]: await 
        sarch_start(pdat, contxt)
    lif txt in ["⚙️ مدیریت فیلدها"]: await 
        manag_filds_start(pdat, contxt)
    lif txt in ["🎨 تغییر تم"]: await 
        chang_thm_start(pdat, contxt)
    lif txt in ["📊 آمار"]: await 
        show_statistics(pdat, contxt)
    lif txt in ["🧹 حذف همه"]: await 
        dlt_all_rcords(pdat, contxt)
    lif txt in ["ℹ️ راهنما"]: await 
        show_hlp(pdat, contxt)
    lif txt in ["✅ بله، همه را حذف کن", "❌ 
    لغو"]:
        await confirm_dlt_all(pdat, contxt) 
    ls:
        await pdat.mssag.rply_txt(  "❌ 
دستور نامعتبر است.\n💡 از منوی زیر استفاده 
کنید:",
            rply_markp=gt_kyboard() ) # 
============================ راه‌اندازی ربات 
============================ df main():  """تابع 
اصلی راه‌اندازی ربات"""
    
    print("🚀 راه‌اندازی ربات Excl مدیریت کامل با 
    آپلود فایل...") print("📤 قابلیت جدید: آپلود 
    فایل Excl دلخواه!") print("✅ آماده برای 
    شروع!")
    
 # ایجاد Application application = 
    ApplicationBildr().tokn(BOT_TOKEN).bild()
    
    print("🔧 در حال راه‌اندازی ربات...")
    # ConvrsationHandlr برای اضافه کردن رکورد
    add_convrsation = ConvrsationHandlr( 
        ntry_points=[
            MssagHandlr(filtrs.Rgx("^➕ 
            اضافه کردن$"), add_rcord_start)
        ], stats={ ADD_DATA: 
            [MssagHandlr(filtrs.TEXT & 
            ~filtrs.COMMAND, 
            add_rcord_procss)]
        },
        fallbacks=[CommandHandlr("cancl", 
        cancl)]
    )
    # ConvrsationHandlr برای آپلود فایل - اینجا 
    # مشکل اصلی حل شده! 💪
    pload_convrsation = ConvrsationHandlr( 
        ntry_points=[
            MssagHandlr(filtrs.Rgx("^📤 
            آپلود فایل Excl$"), 
            pload_fil_start)
        ], stats={ UPLOAD_FILE: [  # پشتیبانی از 
هر دو حالت: دکمه و تایپ متن 🔥
                MssagHandlr( filtrs.TEXT & ( 
                        filtrs.Rgx("^🔄 
                        جایگزینی کامل فایل 
                        فعلی$") | 
                        filtrs.Rgx("^➕ ادغام 
                        با فایل موجود$") | 
                        filtrs.Rgx("^❌ لغو$")
                    ), pload_fil_procss ), 
                MssagHandlr(filtrs.Docmnt.ALL, 
                handl_ploadd_fil)
            ]
        },
        fallbacks=[CommandHandlr("cancl", 
        cancl)]
    )
    # ConvrsationHandlr برای ویرایش
    dit_convrsation = ConvrsationHandlr( 
        ntry_points=[
            MssagHandlr(filtrs.Rgx("^✏️ 
            ویرایش$"), dit_start)
        ], stats={ EDIT_ROW: 
            [MssagHandlr(filtrs.TEXT & 
            ~filtrs.COMMAND, dit_row_slct)], 
            EDIT_FIELD: 
            [MssagHandlr(filtrs.TEXT & 
            ~filtrs.COMMAND, 
            dit_fild_slct)], EDIT_VALUE: 
            [MssagHandlr(filtrs.TEXT & 
            ~filtrs.COMMAND, dit_val_apply)]
        },
        fallbacks=[CommandHandlr("cancl", 
        cancl)]
    )
    # ConvrsationHandlr برای حذف
    dlt_convrsation = ConvrsationHandlr( 
        ntry_points=[
            MssagHandlr(filtrs.Rgx("^🗑️ 
            حذف$"), dlt_start)
        ], stats={ DELETE_ROW: 
            [MssagHandlr(filtrs.TEXT & 
            ~filtrs.COMMAND, 
            dlt_row_procss)]
        },
        fallbacks=[CommandHandlr("cancl", 
        cancl)]
    )
    # ConvrsationHandlr برای جستجو
    sarch_convrsation = ConvrsationHandlr( 
        ntry_points=[
            MssagHandlr(filtrs.Rgx("^🔍 
            جستجو$"), sarch_start)
        ], stats={ SEARCH_QUERY: 
            [MssagHandlr(filtrs.TEXT & 
            ~filtrs.COMMAND, sarch_procss)]
        },
        fallbacks=[CommandHandlr("cancl", 
        cancl)]
    )
    # ConvrsationHandlr برای مدیریت فیلدها
    manag_filds_convrsation = 
    ConvrsationHandlr(
        ntry_points=[ 
            MssagHandlr(filtrs.Rgx("^⚙️ 
            مدیریت فیلدها$"), 
            manag_filds_start)
        ], stats={ MANAGE_FIELDS: 
            [MssagHandlr(filtrs.TEXT & 
            ~filtrs.COMMAND, 
            manag_filds_procss)], ADD_FIELD: 
            [MssagHandlr(filtrs.TEXT & 
            ~filtrs.COMMAND, 
            add_fild_procss)], 
            DELETE_FIELD_SELECT: 
            [MssagHandlr(filtrs.TEXT & 
            ~filtrs.COMMAND, 
            dlt_fild_procss)]
        },
        fallbacks=[CommandHandlr("cancl", 
        cancl)]
    )
    # ConvrsationHandlr برای تغییر تم
    thm_convrsation = ConvrsationHandlr( 
        ntry_points=[
            MssagHandlr(filtrs.Rgx("^🎨 
            تغییر تم$"), chang_thm_start)
        ], stats={ CHANGE_THEME: 
            [MssagHandlr(filtrs.TEXT & 
            ~filtrs.COMMAND, 
            chang_thm_procss)]
        },
        fallbacks=[CommandHandlr("cancl", 
        cancl)]
    )  # اضافه کردن تمام handlr ها 
    application.add_handlr(CommandHandlr("start", 
    start))
    
    # ConvrsationHandlr ها - ترتیب مهم است!
    application.add_handlr(pload_convrsation) 
    # اول آپلود
    application.add_handlr(add_convrsation) # 
    بعد اضافه کردن 
    application.add_handlr(dit_convrsation) # 
    ویرایش 
    application.add_handlr(dlt_convrsation) 
    # حذف
    application.add_handlr(sarch_convrsation) 
    # جستجو
    application.add_handlr(manag_filds_convrsation) 
    # مدیریت فیلدها
    application.add_handlr(thm_convrsation) # 
    تغییر تم
    # MssagHandlr های تکی برای عملیات ساده
    application.add_handlr(MssagHandlr(filtrs.Rgx("^📋 
    نمایش همه$"), show_all_rcords)) 
    application.add_handlr(MssagHandlr(filtrs.Rgx("^📁 
    دریافت فایل$"), snd_xcl_fil)) 
    application.add_handlr(MssagHandlr(filtrs.Rgx("^📊 
    آمار$"), show_statistics)) 
    application.add_handlr(MssagHandlr(filtrs.Rgx("^🧹 
    حذف همه$"), dlt_all_rcords)) 
    application.add_handlr(MssagHandlr(filtrs.Rgx("^ℹ️ 
    راهنما$"), show_hlp))
    
    # Handlr کلی برای پیام‌های متنی (آخرین 
    # handlr)
    application.add_handlr(MssagHandlr(filtrs.TEXT 
    & ~filtrs.COMMAND, handl_txt_mssags))
 # راه‌اندازی ربات print("🎯 ربات آماده است!") 
    print("🔗 ربات را در تلگرام راه‌اندازی 
    کنید...")
    
    try: 
    application.rn_polling(drop_pnding_pdats=Tr) 
    xcpt KyboardIntrrpt:
        print("\n⏹️ ربات متوقف شد.") xcpt 
    Excption as :
        print(f"❌ خطا در راه‌اندازی: {}") 
        loggr.rror(f"Bot startp rror: {}")
if __nam__ == "__main__":
    main()

# Univrsal Fallback Handlr
async df nivrsal_fallback(pdat: Updat, contxt: ContxtTyps.DEFAULT_TYPE):
    """Fallback handlr برای خروج از هر stat گیرکرده"""
    await pdat.mssag.rply_txt(
        "❌ **خطا در درک دستور!**\n\n"
        "🏠 بازگشت به منوی اصلی...\n"
        "💡 لطفاً از دکمه‌های زیر استفاده کنید:",
        rply_markp=gt_kyboard()
    )
    contxt.sr_data.clar()
    rtrn ConvrsationHandlr.END

