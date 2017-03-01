import { Component, OnInit } from '@angular/core';
import '../static/css/global-layout.css';
import '@angular/material/core/theming/prebuilt/deeppurple-amber.css';

import { User } from './user.model';
import { UserService } from './user.service';

@Component({
    selector: 'firebot',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
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
