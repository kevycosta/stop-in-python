import { Inject } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivateFn, Router, RouterStateSnapshot } from '@angular/router';
import { CookieService } from '../services/cookie.service';

export const authGuard: CanActivateFn = (
  route:ActivatedRouteSnapshot, 
  state:RouterStateSnapshot
) => {
  const router: Router = Inject(Router);
  const cookieService: CookieService = Inject(CookieService);
  const protectedRoutes: string[] = ['/main'];

  return protectedRoutes.includes(state.url) && cookieService.checkCookie('authToken') 
    ? router.navigate(['/login']) 
    : false; 
};
