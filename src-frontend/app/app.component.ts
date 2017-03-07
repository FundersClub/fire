import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { Router, NavigationEnd, ActivatedRoute } from '@angular/router';
import { Title } from '@angular/platform-browser';

import 'rxjs/add/operator/filter';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/mergeMap';

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
        private activatedRoute: ActivatedRoute,
        private router: Router,
        private titleService: Title,
        private userService: UserService
    ) {}

    ngOnInit() {
        this.userService.userData.then((user) => {
            this.user = user;
        });

        // Update page title during navigation
        this.router.events
            .filter(event => event instanceof NavigationEnd)
            .map(() => this.activatedRoute)
            .map(route => {
                while (route.firstChild) {
                    route = route.firstChild
                }
                return route;
            })
            .filter(route => route.outlet === 'primary')
            .mergeMap(route => route.data)
            .subscribe((event) => {
                let title = !!event['title'] ? (event['title'] + ' | Fire') : 'Fire';
                this.titleService.setTitle(title)
            });
    }
}
