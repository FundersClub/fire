import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Repository } from './repository.model';

@Component({
    selector: 'manage-address',
    templateUrl: './manage-address.component.html',
    styleUrls: ['./manage-address.component.css']
})
export class ManageAddressComponent implements OnInit {
    repository: Repository;
    inEditMode: boolean = false;

    constructor(
        private route: ActivatedRoute,
    ) {}

    ngOnInit() {
        this.route.data.subscribe((data: { repository: Repository }) => {
            this.repository = data.repository;
        });
    }
}
