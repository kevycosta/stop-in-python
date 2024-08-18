import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class CookieService {

  constructor() {}

  checkCookie(name: string): boolean {
    return document.cookie.split(';').some(cookie => {
      return cookie.trim().startsWith(`${name}=`);
    });
  }

  getCookie(name: string): string | null | undefined {
    const b = document.cookie.match(`(^|;)\\s*${name}\\s*=\\s*([^;]+)`);
    return b ? b.pop() : null;
  }

  setCookie(name: string, value: string): void {
    let expires = '';
    
    const date = new Date();
    date.setTime(date.getTime() + (60 * 24 * 60 * 60 * 1000));
    expires = `; expires=${date.toUTCString()}`;
    
    const cookie = `${name}=${value}${expires}; path=/`;
    document.cookie = cookie;
  }

  deleteCookie(name: string): void {
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:01 GMT; path=/`;
  }
}
