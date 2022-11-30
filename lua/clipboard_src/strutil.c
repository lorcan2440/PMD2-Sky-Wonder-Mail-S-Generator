#include <string.h>
#include <tchar.h>
#include "stdmacro.h"
// get pointer to the last char (before '\0')
TCHAR* str_lastchar (const TCHAR* str){
	TCHAR* psz = ((TCHAR*)str);
	while(*psz++);
	psz -= 2;
	return(psz>((TCHAR*)str)?psz:((TCHAR*)str));
}
// get the ptr to filename of path
TCHAR* str_path_filenameptr(const TCHAR* str){
	TCHAR* pcsz = str_lastchar(str);
	while(pcsz >= str && !ISSLASH(pcsz[0]))--pcsz;
	return(++pcsz);
}
// trim trailing char
TCHAR* str_trim_trailingchar(TCHAR* str, int chr){
	TCHAR* pcsz = str_lastchar(str);
	while(pcsz >= str && pcsz[0] == chr)(pcsz--)[0]=0;
	return(str);
}
// trim trailing slashes "/" "\"
TCHAR* str_trim_trailingslashes(TCHAR* str){
	TCHAR* pcsz = str_lastchar(str);
	while(pcsz >= str && ISSLASH(pcsz[0]))(pcsz--)[0]=0;
	return(str);
}
// get the parent folder of path
TCHAR* str_path_toparent(TCHAR* str){
	TCHAR* pcsz = str_lastchar(str);
	while(pcsz >= str && !ISSLASH(pcsz[0]) && pcsz[0]!=':')(pcsz--)[0]=0;
	if(ISSLASH(pcsz[0]))pcsz[0]=0;
	return(str);
}
// get the extension of path
TCHAR* str_path_extptr(TCHAR* str){
	TCHAR* pcsz = str_lastchar(str);
	while(pcsz >= str && '.'==pcsz[0])--pcsz;
	return(pcsz);
}
// add an ending "\"
TCHAR* str_path_qualify(TCHAR* str){
	TCHAR* pcsz = str_lastchar(str);
	if(!ISSLASH(pcsz[0])){
		pcsz[1]=_T('\\');
		pcsz[2]=0;
	}
	return(str);
}
// check str if it has wild card char
int str_iswild(const TCHAR* str){
	while(str[0] && (str[0] != '*' && str[0] != '?'))str++;
	return (str[0] == '*' || str[0] == '?');
}
//
int str_has_crlf(register const TCHAR* str){
	while (*str){
		if (*str++ == '\r' && *str == '\n'){
			return 1;
		}
	}
	return 0;
}

void str_crlf_to_lf(TCHAR* str){
	register unsigned int i = 0, j = 0;
	while (str[i] != '\0'){
		if (str[i] == '\r' && str[i+1] == '\n'){
			i++;
		}
		str[j++] = str[i++];
	}
	str[j] = '\0';// Terminate
}

int str_extra_cr_len(const TCHAR *str){
	int j = 0;
	while (*str){
		if(*str++ == '\n')j++;
	}
	return j;
}

void str_lf_to_crlf(const TCHAR *src, TCHAR *dst){
	while (*src){
		if (*src == '\n')*dst++ = '\r';
		*dst++ = *src++;
	}
	*dst = '\0';
}

int str_icmp_ascii(const char * dst, const char * src){
	int f, l;
	do {
	if ( ((f = (unsigned char)(*(dst++))) >= 'A') &&	(f <= 'Z') )
		f -= 'A' - 'a';
	if ( ((l = (unsigned char)(*(src++))) >= 'A') &&	(l <= 'Z') )
		l -= 'A' - 'a';
	} while ( f && (f == l) );
	return(f - l);
}

// 
void str_path_concat3(TCHAR* path, const TCHAR *path1, const TCHAR *path2, const TCHAR *path3){
	register const _TSCHAR *p;
	if ((p = path1) != NULL && *p) {
		do{*path++ = *p++;}	while (*p);
		if (((path2 && *path2 && !ISSLASH(*path2))||(path3 && *path3 && !ISSLASH(*path3))) && !ISSLASH(p[-1]))
			*path++ = _T('\\');
	}
	if ((p = path2) != NULL && *p) {
		do{*path++ = *p++;}	while (*p);
		if ((path3 && *path3 && !ISSLASH(*path3)) && !ISSLASH(p[-1]))
			*path++ = _T('\\');
	}
	if ((p = path3) != NULL && *p) {
		do{*path++ = *p++;}	while (*p);
	}
	*path = _T('\0');
}

TCHAR* str_path_relative(TCHAR* relative, TCHAR *thisname, TCHAR *thatname ){
	TCHAR *i_this;
	TCHAR *i_that;
	TCHAR *i_this_slash = NULL;
	TCHAR *i_that_slash = NULL;
	TCHAR *xslash = _tcschr(thisname, '\\') > _tcschr(thisname, '/') ? _T("\\"):_T("/");

	relative[0] = '\0';


	for ( i_this = thisname, i_that = thatname;
		( *i_this && *i_that ) && ( (*i_this == *i_that)||(ISSLASH(*i_this)&& ISSLASH(*i_that)) );
		++i_this, ++i_that )
	{
		if ( ISSLASH(*i_this) ){
			i_this_slash = i_this;
		}
		if ( ISSLASH(*i_this) ){
			i_that_slash = i_that;
		}
	}

	if ( i_this_slash && i_that_slash )
	{
		int                 this_slashes_left = 0;
		int                 that_slashes_left = 0;
		TCHAR               *i_c;

		for ( i_c = i_this_slash + 1; *i_c; ++i_c )
		{
			if (ISSLASH(*i_c))
			{
				++this_slashes_left;
			}
		}

		for ( i_c = i_that_slash + 1; *i_c; ++i_c )
		{
			if (ISSLASH(*i_c))
			{
				++that_slashes_left;
			}
		}

		if( this_slashes_left ){
			int                 i;
			for ( i = 0; i < this_slashes_left; ++i ){
			_tcscat( relative, _T("..") );
			_tcscat( relative, xslash);
			/* ../ */
			}
			_tcscat( relative, i_that_slash + 1 );
		}else if ( that_slashes_left ){
			/* !this_slashes_left && that_slashes_left */
			_tcscat( relative, _T(".") );
			_tcscat( relative, xslash);
			/* ./ */
			_tcscat( relative, i_that_slash + 1 );

		}else{
			/* !this_slashes_left && !that_slashes_left */
			_tcscat( relative, _T(".") );
			_tcscat( relative, xslash);
			/* ./ */
			_tcscat( relative, i_that_slash + 1 );
		}
	}
	return relative;
}