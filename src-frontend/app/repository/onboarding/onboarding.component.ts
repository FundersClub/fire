import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd, ActivatedRoute } from '@angular/router';

import 'rxjs/add/operator/filter';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/mergeMap';

@Component({
    styleUrls: ['./onboarding.component.scss'],
    templateUrl: './onboarding.component.html'
})
export class OnboardingComponent implements OnInit {
    progressBarValue = 0;

    constructor(
        private router: Router,
        private activatedRoute: ActivatedRoute
    ) {}

    ngOnInit() {
        this.router.events
            // Only want end events...
            .filter(event => event instanceof NavigationEnd)
            // Get the activatedRoute property of those...
            .map(() => this.activatedRoute)
            // Dig into tree to get child route being shown...
            .map(route => {
                while (route.firstChild) {
                    route = route.firstChild
                }
                return route;
            })
            // Handle multi-outlet routes...
            .filter(route => route.outlet === 'primary')
            // Get data property...
            .mergeMap(route => route.data)
            // Update progress bar!
            .subscribe((event) => this.progressBarValue = event['progressBarValue'] || 0);
    }
}
