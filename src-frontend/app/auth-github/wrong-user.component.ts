import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Repository } from '../repository/repository.model';
import { User } from '../auth-github/user.model';

@Component({
    templateUrl: './wrong-user.component.html'
})
export class WrongUserComponent implements OnInit {
    repository: Repository;
    user: User;

    constructor(private route: ActivatedRoute) {}

    ngOnInit() {
        let data = this.route.snapshot.data as {
            repository: Repository,
            user: User,
        };
        this.repository = data.repository;
        this.user = data.user;
    }
}
