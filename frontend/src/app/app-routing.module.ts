import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MainComponent } from './pages/main/main.component';
import { authGuard } from './guards/auth.guard';
import { LoginComponent } from './pages/login/login.component';

const routes: Routes = [
  {path: "main", component: MainComponent, pathMatch: "full"},
  {path: "login", component: LoginComponent, pathMatch: "full"},
  {path: "**", pathMatch: "full", redirectTo:"main", canActivate:[authGuard]},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
