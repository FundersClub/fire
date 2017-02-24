import { Component, OnInit } from '@angular/core';

import { User }                from './user.model';
import { UserService }         from './user.service';

@Component({
    selector: 'repository-list',
    templateUrl: './repository-list.component.html',
})
export class RepositoryListComponent implements OnInit {
    user: User;

    constructor(
        private userService: UserService
    ) {}


    ngOnInit(): void {
        this.userService
            .getUserData()
            .then(user => this.user = user);
    }


}
