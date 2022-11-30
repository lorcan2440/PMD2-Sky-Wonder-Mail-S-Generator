#ifndef __LUA_REG__
#define __LUA_REG__

int clip_settext(lua_State *L);
int clip_settextu(lua_State *L);
int clip_setdata(lua_State *L);
int clip_gettextu(lua_State *L);
int clip_gettext(lua_State *L);
int clip_getdata(lua_State *L);
int clip_getformats(lua_State *L);
int clip_formatname(lua_State *L);
int clip_getfiles(lua_State *L);
int clip_empty(lua_State *L);
int clip_isformatavailable(lua_State *L);
int clip_registerformat(lua_State *L);
int clip_textformat(lua_State *L);

extern luaL_reg lreg_clip[];
#ifdef LUA_REG_DEFINE_EXTERNS
luaL_reg lreg_clip[] = {
{"settext",clip_settext},
{"settextu",clip_settextu},
{"setdata",clip_setdata},
{"gettextu",clip_gettextu},
{"gettext",clip_gettext},
{"getdata",clip_getdata},
{"getformats",clip_getformats},
{"formatname",clip_formatname},
{"getfiles",clip_getfiles},
{"empty",clip_empty},
{"isformatavailable",clip_isformatavailable},
{"registerformat",clip_registerformat},
{"textformat",clip_textformat},
{0,0}};// Total:13
#endif

#endif //__LUA_REG__