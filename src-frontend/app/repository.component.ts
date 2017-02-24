import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute, Params } from '@angular/router';
import 'rxjs/add/operator/switchMap';

@Component({
    selector: 'repository',
    templateUrl: './repository.component.html',
})
export class RepositoryComponent implements OnInit {
    private id: string;

    constructor(
        private route: ActivatedRoute,
        private router: Router
    ) {}

    ngOnInit() {
        this.id = this.route.snapshot.params['id'];
        // this.route.params
        //     .switchMap((params: Params) => this.id = params['id'])
        //     .subscribe((hero: Hero) => this.hero = hero);
    }
}
