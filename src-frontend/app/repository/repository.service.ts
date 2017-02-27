import { Injectable } from '@angular/core';
import { Http } from '@angular/http';

import 'rxjs/add/operator/toPromise';

import { Repository } from './repository.model';

const ERROR_MESSAGE = {
    "email_slug": [
        "This field may not be blank."
    ]
}

@Injectable()
export class RepositoryService {
    private repositories: Repository[] = [];

    constructor(
        private http: Http
    ) {}

    add(repository: Repository) {
        this.repositories.push(repository);
    }

    all() {
        return this.repositories;
    }

    getByDisplayName(login: string, name: string) {
        return this.repositories.find(
            (repo) => repo.login == login && repo.name == name
        );
    }

    getByUrl(url: string) {
        return this.repositories.find((repo) => repo.url == url);
    }

    updateAddress(repository: Repository, newAddress: string): Promise<any> {
        let data = {email_slug: newAddress};
        return new Promise((resolve, reject) => {
            this.http.patch(repository.url, data).toPromise()
                .then((response) => {
                    const repo = response.json() as Repository;
                    // Update repo entry in list with any new serverside data.
                    const index = this.repositories.findIndex((r) => r.url == repo.url);
                    if (index > -1) {
                        this.repositories[index] = repo;
                    }
                    resolve(repo);
                })
                .catch((error) => {
                    let err = error.json();
                    if (typeof err == 'object' && typeof err['email_slug'] == 'object') {
                        reject(err['email_slug'][0])
                    } else {
                        reject('Could not update email');
                    }
                });
            }
        );
    }
}
