import { Component, OnInit, ViewChild, Input } from '@angular/core';
import { NgForm } from '@angular/forms';

import { EmailMap } from './email-map.model';
import { Repository } from '../repository.model';
import { RepositoryService } from '../repository.service';

@Component({
    selector: 'email-map-add',
    styleUrls: ['./email-map-add.component.scss'],
    templateUrl: './email-map-add.component.html',
})
export class EmailMapAddComponent implements OnInit {
    @Input() repository: Repository;
    @ViewChild(NgForm) private form: NgForm;
    emailMap: EmailMap;
    error = {};

    constructor(
        private repositoryService: RepositoryService
    ) {}

    ngOnInit() {
        this.emailMap = new EmailMap('', '', this.repository.url);
    }

    save() {
        this.error = {};
        this.repositoryService.addEmailMap(this.emailMap)
            .then((emailMap) => this.form.resetForm())
            .catch((error: any) => this.error = error);
    }
}
