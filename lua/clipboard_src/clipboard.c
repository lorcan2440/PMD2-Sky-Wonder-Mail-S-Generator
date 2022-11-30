#ifdef _LUAMSVC
#	include <luamsvc.h>
#endif

#include <windows.h>

#include <assert.h>
#define lua_assert assert

#include <lua.h>
#include <lualib.h>
#include <lauxlib.h>

#include "stdmacro.h"
#include "luamacro.h"
#include "luawinmacro.h"

#include "win_trace.h"
#include "lua_tstring.h"
#include "luawin_dllerror.h"
#include "strutil.h"

#define LUA_REG_DEFINE_EXTERNS
#include "luareg.h"

typedef struct KVDATA{
	const char * name;
	size_t data;
} KVDATA, *PKVDATA;

typedef struct _CB_DATA{
	UINT textfmt;
}CB_DATA, *PCB_DATA;

BOOL APIENTRY DllMain( HANDLE hModule, DWORD ul_reason_for_call, LPVOID lpReserved){
	UNUSED(hModule);
	UNUSED(ul_reason_for_call);
	UNUSED(lpReserved);
    return TRUE;
}

#define lrk_cbdata	 "{afx/cbdata}"

void lua_pushcbdata(lua_State *L){
	lua_pushstring(L, lrk_cbdata);
	lua_rawget(L, LUA_REGISTRYINDEX);
	if(lua_isnil(L,-1)){		//STACK:...<retval>#
		CB_DATA* pcbd;
		lua_pop(L, 1);			//STACK:...#
		pcbd = (CB_DATA*)lua_newuserdata(L, sizeof(CB_DATA));
		pcbd->textfmt = CF_TEXT;
		lua_pushstring(L, lrk_cbdata);
		lua_pushvalue(L, -2);
		lua_rawset(L, LUA_REGISTRYINDEX);
	}
	lua_assert(lua_isfulluserdata(L, -1));
}

#define lua_getcbdata(L) (((CB_DATA*)lua_touserdata(L, lua_upvalueindex(1))))
__declspec(dllexport) int luaopen_clipboard(lua_State *L){
	lua_pushcbdata(L);
	luaL_openlib(L, "clipboard", lreg_clip, 1);
	return 1;
}

static KVDATA cffmt[] = {
#ifndef CF_HDROP
#	define CF_HDROP		15
#endif
#ifndef CF_LOCALE
#	define CF_LOCALE	16
#endif
#ifndef CF_DIBV5
#	define CF_DIBV5		17
#endif
	{"text", CF_TEXT},
	{"ansi", CF_TEXT},
	{"bitmap", CF_BITMAP},
	{"metafilepict", CF_METAFILEPICT},
	{"sylk", CF_SYLK},
	{"dif", CF_DIF},
	{"tiff", CF_TIFF},
	{"oemtext", CF_OEMTEXT},
	{"oem", CF_OEMTEXT},
	{"dib", CF_DIB},
	{"palette", CF_PALETTE},
	{"pendata", CF_PENDATA},
	{"riff", CF_RIFF},
	{"wave", CF_WAVE},
	{"unicodetext", CF_UNICODETEXT},
	{"enhmetafile", CF_ENHMETAFILE},
	{"hdrop", CF_HDROP},
	{"locale", CF_LOCALE},
	{"dibv5", CF_DIBV5},
	{"ownerdisplay", CF_OWNERDISPLAY},
	{"dsptext", CF_DSPTEXT},
	{"dspbitmap", CF_DSPBITMAP},
	{"dspmetafilepict", CF_DSPMETAFILEPICT},
	{"dspenhmetafile", CF_DSPENHMETAFILE},
	{0,0}
};

UINT clip_aux_getformat(lua_State *L, int i){
	if(lua_isrealstring(L,i)){
		const char * psz = lua_tostring(L, i);
		PKVDATA pkvd = cffmt;
		while(pkvd->name && strcmp(psz, pkvd->name))pkvd++;
		if(pkvd->name) return (UINT)pkvd->data;
	}
	return lua_checkUINT(L, i);
}

UINT clip_aux_gettextformat(lua_State *L, int i){
	UINT fmt = clip_aux_getformat(L, i);
	if(!(fmt == CF_TEXT || fmt == CF_OEMTEXT)){
		luaL_argerror(L, i, "wrong format");
	}
	return fmt;
}

const void * clip_aux_getdata(lua_State *L, int i, size_t * plen){
#if LUA_VERSION_NUM >= 501
	if(lua_isfulluserdata(L,i)){
		if(plen){
			*plen = lua_objlen(L,i);
		}
		return lua_touserdata(L,i);
	}else
#endif
	{
		return lua_checklstring(L, i, plen);
	}
}
int cbsetdata(UINT format, const void * pdata, DWORD cb){//
	int ok = 0;
	HGLOBAL hMem = GlobalAlloc(GMEM_MOVEABLE|GMEM_DDESHARE, cb);
	if (hMem != NULL){
		if(OpenClipboard(NULL)){
			PVOID pData = GlobalLock(hMem);
			if(pData != NULL){
				CopyMemory(pData, pdata, cb);
			}
			GlobalUnlock(hMem);
			if(EmptyClipboard()){
				if(SetClipboardData(format, hMem)){
					ok = 1;
				}else{
					GlobalFree(hMem);
				}
			}
			CloseClipboard();
		}else{
			GlobalFree(hMem);
		}
	}
	return ok;
}

const char * aux_nl_conv(lua_State *L, const char * s){
	int a;
	if(s && *s && (a = str_extra_cr_len(s)) > 0){
		size_t c = strlen(s);
		char * sz = lua_alloc_char(L, c+a+1);
		str_lf_to_crlf(s, sz);
		return sz;
	}else{
		return s;
	}
}

int aux_clip_settext(lua_State *L, const char * sz, UINT fmt, int cvnl){
	size_t uLen = 0;
	const void * pdata = NULL;
	if(cvnl){
		sz = aux_nl_conv(L, sz);
	}
	uLen = strlen(sz);

	if(fmt == CF_UNICODETEXT){
		uLen = (lua_utf8towcsZ(L, sz, (int)uLen) + 1)*sizeof(WCHAR);
		pdata = (const void *)lua_tostring(L, -1);
	}else{
		uLen++;// plus the null byte!
		pdata = (const void *)sz;
	}
	LUA_LAST_DLL_ERROR_ASSERT_PUSHBOOL(L, cbsetdata(fmt, pdata, (DWORD)uLen));
	return 1;
}

int clip_settext(lua_State *L){//clip.settext
	CB_DATA* pcbd = lua_getcbdata(L);
	return aux_clip_settext(L
		, lua_checkstring(L, 1)
		, lua_isnoneornil(L,2)?pcbd->textfmt:clip_aux_gettextformat(L,2)
		, lua_optbool(L, 3, 1)
		);
}

int clip_settextu(lua_State *L){//clip.settextu
	return aux_clip_settext(L
		, lua_checkstring(L, 1)
		, CF_UNICODETEXT
		, lua_optbool(L, 2, 1)
		);
}

int clip_setdata(lua_State *L){//clip.setdata
	size_t uLen = 0;
	const void *pdata = clip_aux_getdata(L, 1, &uLen);
	UINT fmt = clip_aux_getformat(L, 2);
	int ret = cbsetdata(fmt, pdata, (DWORD)uLen);
	LUA_LAST_DLL_ERROR_ASSERT_PUSHBOOL(L, ret);
	return 1;
}
const WCHAR *lua_mbsztowcs(lua_State *L, UINT CodePage, LPCSTR pmbs, DWORD dwFlags){
	int x = 0;
	WCHAR *szw = NULL;
	if(!pmbs)return NULL;
	if(*pmbs == 0)return L"";
	x = MultiByteToWideChar(CodePage, dwFlags, pmbs, -1, 0, 0);
	if(x++ > 0 && NULL != (szw = lua_alloc_wchar(L, x))
	&& (szw[0]=0, MultiByteToWideChar(CodePage, dwFlags, pmbs, -1, szw, x)) > 0){
		return szw;
	}
	return NULL;
}
const char *lua_wcsztombs(lua_State *L, UINT CodePage, LPCWSTR pwcs, DWORD dwFlags){
	int x = 0;
	char *sza = NULL;
	if(!pwcs)return NULL;
	if(*pwcs == 0)return "";
	x = WideCharToMultiByte(CodePage, dwFlags, pwcs, -1, 0, -1, 0, 0);
	if(x++ > 0 && NULL != (sza = lua_alloc_char(L, x))
	&& (*sza=0, WideCharToMultiByte(CodePage, dwFlags, pwcs, -1, sza, x, 0, 0) > 0)){
		return sza;
	}
	return NULL;
}

int aux_clip_gettext(lua_State *L, UINT fmt, int convert_crlf_to_lf, int convert_to_utf8){
	int ok = 0;
	assert(fmt == CF_TEXT || fmt == CF_UNICODETEXT || fmt == CF_OEMTEXT);
	lua_settop(L,0);
	if(OpenClipboard(NULL)){
		HGLOBAL hClipMem = GetClipboardData(fmt);
		if(hClipMem == NULL && fmt != CF_TEXT){
			fmt = CF_TEXT;
			hClipMem = GetClipboardData(fmt);
		}
		if(hClipMem){
			PVOID pClipMem = GlobalLock(hClipMem);
			if(pClipMem != NULL){
				if(convert_to_utf8){
					const WCHAR *szw = NULL;
					if(fmt == CF_OEMTEXT || fmt == CF_TEXT){
						szw = lua_mbsztowcs(L
							, (fmt == CF_OEMTEXT)?CP_OEMCP:CP_ACP
							, (char *)pClipMem, 0);
					}else{
						szw = (const WCHAR *)pClipMem;
					}
					if(szw){lua_wcstoutf8(L, szw, wcslen(szw));ok = 1;}
				}else{
					const char *sz = NULL;
					if(fmt == CF_UNICODETEXT){
						sz = lua_wcsztombs(L, CP_ACP, (WCHAR *)pClipMem, 0);
					}else{
						sz = (const char *)pClipMem;
					}
					if(sz){lua_pushstring(L, sz);ok = 1;}
				}
			}
			GlobalUnlock(hClipMem);
		}
		CloseClipboard();
	}
	if(ok){
		const char *s = lua_tostring(L, -1);
		if(s && convert_crlf_to_lf && str_has_crlf(s)){
			char * t = lua_alloc_char(L, strlen(s) + 1);
			str_crlf_to_lf(strcpy(t, s));
			lua_pushstring(L, t);
		}
	}else{
		lua_pushnil(L);
	}
	return 1;
}


int clip_gettextu(lua_State *L){//clip.gettextu
	return aux_clip_gettext(L
		, CF_UNICODETEXT
		, lua_optbool(L, 1, 1), 1);
}

int clip_gettext(lua_State *L){//clip.gettext
	CB_DATA* pcbd = lua_getcbdata(L);
	return aux_clip_gettext(L
		, (lua_isnoneornil(L,1)?pcbd->textfmt:clip_aux_gettextformat(L,1))
		, lua_optbool(L, 2, 1), 0);
}

int clip_getdata(lua_State *L){//clip.getdata
	int ok = 0;
	UINT fmt = clip_aux_getformat(L, 1);
	if(OpenClipboard(NULL)){
		HGLOBAL hClipMem = GetClipboardData(fmt);
		if(hClipMem){
			PVOID pClipMem = GlobalLock(hClipMem);
			SIZE_T cb = GlobalSize(hClipMem);
			if(pClipMem != NULL){
				//if(lua_isnoneornil(L, 2)){
					lua_pushlstring(L, (const char *)pClipMem, cb);
				//}else{
				//	PBYTE pdata = (PBYTE)pClipMem;
				//	luaL_checktype(L, 2, LUA_TFUNCTION);
				//}
				ok = 1;
			}
			GlobalUnlock(hClipMem);
		}
		CloseClipboard();
	}
	if(!ok)lua_pushnil(L);
	return 1;
}



int clip_getformats(lua_State *L){//clip.getformats
	if(OpenClipboard(GetClipboardOwner())){
		UINT uFmt = 0;
		int i = 0;
		lua_newtable(L);
		while((uFmt = EnumClipboardFormats(uFmt)) != 0){
			++i;
			lua_rawset_ii(L, -2, i, uFmt);
		}
		CloseClipboard();
	}else{
		lua_pushnil(L);
	}
	return 1;
}

int clip_formatname(lua_State *L){//clip.formatname
	UINT fmt = lua_checkUINT(L, 1);
	PTSTR psz = lua_alloc_tchar(L, MAX_PATH);
	if(GetClipboardFormatName(fmt, psz, MAX_PATH-1)){
		lua_pushtstring(L, psz);
	}else{
		lua_pushnil(L);
	}
	return 1;
}
//docok
#include <shellapi.h>
int clip_getfiles(lua_State *L){//clip.getfiles
	HGLOBAL	hMem = NULL;
	HDROP	hDrop = NULL;
	TCHAR tchbuf[MAX_PATH];
	int c = 0, i;
	if(OpenClipboard(NULL)){
		if((hMem = GetClipboardData(CF_HDROP)) != NULL){
			if(	(hDrop = (HDROP)GlobalLock(hMem)) != NULL){
				if((c = DragQueryFile(hDrop, (UINT)-1, NULL, 0)) != 0){
					lua_createtable(L, c, 0);
					for(i = 0; i < c && DragQueryFile(hDrop, i, tchbuf, MAX_PATH); i++) {
						lua_rawset_it(L, -2, i + 1, tchbuf);
					} 
					DragFinish(hDrop); 
				}
				GlobalUnlock(hMem);
			}
		}
		CloseClipboard();
	}
	if(c == 0){
		lua_pushnil(L);
	}
	return 1;
}
//docok
int clip_empty(lua_State *L){//clip.empty
	if(OpenClipboard(GetClipboardOwner())){
		BOOL ret = EmptyClipboard();
		lua_pushboolean(L, ret);
		CloseClipboard();
	}else{
		lua_pushnil(L);
	}
	return 1;
}

int clip_isformatavailable(lua_State *L){//clip.isformatavailable
	BOOL ret = IsClipboardFormatAvailable(lua_checkint(L, 1));
	lua_pushboolean(L, ret);	
	return 1;
}

int clip_registerformat(lua_State *L){//clip.registerformat
	UINT ret = RegisterClipboardFormat(lua_checktstring(L, 1));
	if(ret){
		lua_pushint(L, ret);
	}else{
		lua_pushnil(L);
	}
	return 1;
}
#if LUA_VERSION_NUM < 501
LUALIB_API int luaL_checkoption (lua_State *L, int narg, const char *def,
                                 const char *const lst[]) {
  const char *name = (def) ? luaL_optstring(L, narg, def) :
                             luaL_checkstring(L, narg);
  int i;
  for (i=0; lst[i]; i++)
    if (strcmp(lst[i], name) == 0)
      return i;
  return luaL_argerror(L, narg,
                       lua_pushfstring(L, "invalid option '%s'", name));
}
#endif
int clip_textformat(lua_State *L){//clip.textformat
	CB_DATA* pcbd = lua_getcbdata(L);
	if(!lua_isnoneornil(L, 1)){
		static int mode[] = {CF_TEXT, CF_TEXT, CF_OEMTEXT, CF_UNICODETEXT};
		static char *const modenames[] = {"ansi", "text", "oem", "utf8", NULL};
		pcbd->textfmt = luaL_checkoption(L, 1, modenames[1], modenames);
	}
	lua_pushint(L, pcbd->textfmt);
	return 1;
}

/*int-clip_priorityformat(lua_State *L){//clip.priorityformat
	const int fc = CountClipboardFormats(VOID);	if(fc > 0){		UINT* pFmt = ((UINT*)lua_newuserdata(L, sizeof(UINT) * fc));		UINT uFmt = 0;
		int i = 0;
		while((uFmt = EnumClipboardFormats(uFmt)) != 0 && i < fc){
			pFmt[i++] = uFmt;
		}		if(i > 0){			GetPriorityClipboardFormat(pFmt, i);		}	}	return 1;
}*/