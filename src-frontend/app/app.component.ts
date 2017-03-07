import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import '../static/css/global-layout.css';

import { User } from './auth-github/user.model';
import { UserService } from './auth-github/user.service';

@Component({
    selector: 'firebot',
    templateUrl: './app.component.html',
    // Make this stylesheet "global" by disabling view encapsulation.
    styleUrls: ['./app.component.scss'],
    encapsulation: ViewEncapsulation.None,
})
export class AppComponent implements OnInit {
    user: User;

    constructor(
        private userService: UserService
    ) {}

    ngOnInit() {
        this.userService.userData.then((user) => {
            this.user = user;
        });
    }
}
