#ifndef __STRUTIL_H__
#define __STRUTIL_H__
#ifdef  __cplusplus
extern "C" {
#endif

TCHAR* str_lastchar (const TCHAR* str);
TCHAR* str_path_filenameptr(const TCHAR* str);
TCHAR* str_trim_trailingchar(TCHAR* str, int chr);
TCHAR* str_trim_trailingslashes(TCHAR* str);
TCHAR* str_path_toparent(TCHAR* str);
TCHAR* str_path_extptr(TCHAR* str);
TCHAR* str_path_qualify(TCHAR* str);
int str_iswild(const TCHAR* str);
void str_path_concat3(TCHAR* path, const TCHAR *path1, const TCHAR *path2, const TCHAR *path3);
TCHAR* str_path_relative(TCHAR* relative, TCHAR *thisname, TCHAR *thatname );

int str_icmp_ascii(const char * dst, const char * src);
void str_crlf_to_lf(TCHAR* str);
void str_lf_to_crlf(const TCHAR *src, TCHAR *dst);
int str_has_crlf(const TCHAR* str);
int str_extra_cr_len(const TCHAR *str);
#ifdef  __cplusplus
}
#endif
#endif //__STRUTIL_H__