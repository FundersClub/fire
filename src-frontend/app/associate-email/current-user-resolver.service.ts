import { Injectable } from '@angular/core';
import { Router, Resolve } from '@angular/router';

import { User } from '../auth-github/user.model';
import { UserService } from '../auth-github/user.service';

@Injectable()
export class CurrentUserResolver implements Resolve<User> {
    constructor(
        private userService: UserService,
        private router: Router
    ) {}

    resolve(): Promise<User> {
        return this.userService.userData
            .then((user) => user)
            .catch((error) => {
                // Failed to pull any user info, very strange...
                this.router.navigate(['/500']);
                return null;
            });
    }
}
