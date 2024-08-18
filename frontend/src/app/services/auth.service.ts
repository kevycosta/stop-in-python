import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { CookieService } from './cookie.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiUrl = 'http://127.0.0.1:5000/';

  constructor(private http: HttpClient, private cookieService: CookieService) { }

  login(username: string, password: string) {
    this.http.post(`${this.apiUrl}/login`, { "username" : username, "password" : password }).subscribe({
      next: (response: any) => {
        if (response.valid) {
          this.cookieService.setCookie('authToken', response.token);
        }
      },
      error: (err:any) => {
        console.log(err);
      }
    })
  }

  isLoggedIn(): boolean {
    return !!this.cookieService.checkCookie('authToken');
  }

  logout(): void {
    this.cookieService.deleteCookie('authToken');
  }
}
