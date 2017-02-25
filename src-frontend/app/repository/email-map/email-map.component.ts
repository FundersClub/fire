import { Component, OnInit, EventEmitter, Input, Output } from '@angular/core';

import { EmailMap } from './email-map.model';

@Component({
    selector: 'email-map',
    templateUrl: './email-map.component.html',
})
export class EmailMapComponent implements OnInit {
    @Input() emailMap: EmailMap;

    constructor() {}

    ngOnInit() {
        console.log('hello');
    }

    save() {
        console.log('save');
    }

    delete() {
        console.log('del');
    }
}
