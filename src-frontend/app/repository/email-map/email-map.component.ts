import { Component, OnInit, ViewChild, EventEmitter, Input, Output } from '@angular/core';
import { NgForm } from '@angular/forms';

import { EmailMap } from './email-map.model';
import { RepositoryService } from '../repository.service';

@Component({
    selector: 'email-map',
    templateUrl: './email-map.component.html',
})
export class EmailMapComponent implements OnInit {
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
        console.log('del');
    }

    showSave() {
        return this.form.dirty;
    }
}
