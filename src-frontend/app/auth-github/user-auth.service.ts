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
                    // For users looking to approve a given repo, send them to
                    // a special page that shows additional information.
                    if (url.startsWith('/approve')) {
                        let uuid = route.params['uuid'];
                        this.router.navigate(
                            [`/authenticate/${uuid}`],
                            {
                                queryParams: {
                                    returnTo: url,
                                }
                            }
                        );
                    } else {
                        this.router.navigate(
                            ['/login'],
                            {
                                queryParams: {
                                    returnTo: url,
                                }
                            }
                        );
                    }
                    return false;
                }
            });
    }
}
