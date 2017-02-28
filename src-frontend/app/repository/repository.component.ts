import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Repository } from './repository.model';

@Component({
    styleUrls: ['./repository.component.css'],
    templateUrl: './repository.component.html',
})
export class RepositoryComponent implements OnInit {
    repo: Repository;

    constructor(
        private route: ActivatedRoute
    ) {}

    ngOnInit() {
        this.route.data.subscribe((data: { repository: Repository }) => {
            this.repo = data.repository;
        });
    }
}
