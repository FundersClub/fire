import { Component } from '@angular/core';

@Component({
    template: `
        <div class="SectionTitle">
            Welcome to fire!
        </div>
        <md-card class="SectionCard">
            <router-outlet></router-outlet>
        </md-card>
    `
})
export class OnboardingComponent {
    constructor() {}
}
