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

    get(login: string, name: string) {
        return this.repositories.find(
            (repo) => repo.login == login && repo.name == name
        );
    }

    // p.map((val) => {if (val == 'one') { return 'oneone' } else return val})

    updateAddress(repository: Repository, newAddress: string): Promise<any> {
        // TODO: Try and PUT the email_slug to the repo's URL
        // let p = this.http.put(repository.url, {email_slug: newAddress})
        //     .toPromise()
        //     .then((response: User) => {
        //       UPDATE ARRAY OR REPOSITORIES WITH NEW DATA
        //     response.json() as User
        // })
        //     .catch(// surface validaiton errors);

        // this.userData = Promise.resolve(USER_DATA);

        // // Update other services.
        // this.userData.then((user: User) => {
        //     // Cache data.
        //     if (user && user.repositories) {
        //         for (let repo of user.repositories) {
        //             this.repositoryService.add(repo);
        //         }
        //     }
        // });

        // Update existing repository object for now
        // (should actually eventually replace it with new obj from server)
        if (newAddress == 'bad') {
            return Promise.reject(ERROR_MESSAGE['email_slug'][0]);
        }

        this.repositories = this.repositories.map((repo) => {
            if (repo.url === repository.url) {
                repo['email_slug'] = newAddress;
                return repo;
            } else {
                return repo;
            }
        });
        return Promise.resolve();
    }
}
