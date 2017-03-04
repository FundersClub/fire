import { Injectable } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';

import { UserService } from './user.service';

@Injectable()
export class UserIsAuthedGuard implements CanActivate {
    constructor(
        private router: Router,
        private userService: UserService,
    ) {}

    canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
        let url = state.url;
        return this.userService.isAuthenticated()
            .then((isAuthed: boolean) => {
                if (isAuthed) {
                    return true;
                } else {
                    this.router.navigate(
                        ['/authenticate'],
                        {
                            queryParams: {
                                returnTo: url,
                            }
                        }
                    );
                    return false;
                }
            });
    }
}
