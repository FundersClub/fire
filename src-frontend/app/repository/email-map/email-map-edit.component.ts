import { Component, OnInit, ViewChild, EventEmitter, Input } from '@angular/core';
import { NgForm } from '@angular/forms';

import { EmailMap } from './email-map.model';
import { RepositoryService } from '../repository.service';

@Component({
    selector: 'email-map-edit',
    templateUrl: './email-map-edit.component.html',
})
export class EmailMapEditComponent implements OnInit {
    @Input() emailMap: EmailMap;
    @ViewChild(NgForm) private form: NgForm;
    originalData: EmailMap;
    error = {};

    constructor(
        private repositoryService: RepositoryService
    ) {}

    ngOnInit() {
        this.originalData = Object.assign({}, this.emailMap);
    }

    save() {
        this.error = {};
        this.repositoryService.updateEmailMap(this.emailMap)
            .then((updatedEM) => this.form.resetForm(updatedEM))
            .catch((error: any) => this.error = error);
    }

    reset() {
        this.form.resetForm(Object.assign({}, this.originalData));
    }

    delete() {
        this.repositoryService.deleteEmailMap(this.emailMap);
    }

    showSave() {
        return this.form.dirty;
    }
}
