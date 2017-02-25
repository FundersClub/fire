import { Injectable } from '@angular/core';
import { CanActivate } from '@angular/router';

import { UserService } from './user.service';

@Injectable()
export class UserIsAuthedGuard implements CanActivate {
    constructor(private userService: UserService) {}

    canActivate() {
        return this.userService.isAuthenticated();
    }
}
