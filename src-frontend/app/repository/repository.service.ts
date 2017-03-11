import { Injectable } from '@angular/core';
import { Http } from '@angular/http';

import 'rxjs/add/operator/toPromise';

import { Repository } from './repository.model';
import { EmailMap } from './email-map/email-map.model';

@Injectable()
export class RepositoryService {
    private repositories: Repository[] = [];

    constructor(
        private http: Http
    ) {}

    add(repository: Repository) {
        // Sanity check to ensure we don't create dupes.
        if (!this.getByUuid(repository.uuid)) {
            this.repositories.push(repository);
        }
    }

    active() {
        return this.repositories.filter((repo) => repo.status == 'active');
    }

    getByDisplayName(login: string, name: string) {
        return this.repositories.find(
            (repo) => repo.login == login && repo.name == name
        );
    }

    getByUrl(url: string) {
        return this.repositories.find((repo) => repo.url == url);
    }

    getByUuid(uuid: string) {
        return this.repositories.find((repo) => repo.uuid == uuid);
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

    updateEmailMap({url, repo, login, email}: EmailMap): Promise<any> {
        const repository = this.getByUrl(repo);
        return new Promise((resolve, reject) => {
            this.http.patch(url, {login, email}).toPromise()
                .then((response) => {
                    const updatedEM = response.json() as EmailMap;
                    // Update repo entry in list with new map data.
                    const index = repository.emailmap_set.findIndex((e) => e.url == url);
                    if (index > -1) {
                        repository.emailmap_set[index] = updatedEM;
                    }
                    resolve(updatedEM);
                })
                .catch((error) => {
                    reject(error.json());
                });
            }
        );
    }

    addEmailMap({repo, login, email}: EmailMap): Promise<any> {
        const repository = this.getByUrl(repo);
        return new Promise((resolve, reject) => {
            this.http.post(repository.urls.emailmap_add, {login, email, repo}).toPromise()
                .then((response) => {
                    const emailMap = response.json() as EmailMap;
                    repository.emailmap_set.push(emailMap);
                    resolve(emailMap);
                })
                .catch((error) => {
                    reject(error.json());
                });
            }
        );
    }

    deleteEmailMap({url, repo}: EmailMap): Promise<any> {
        const repository = this.getByUrl(repo);
        return new Promise((resolve, reject) => {
            this.http.delete(url).toPromise()
                .then(() => {
                    const index = repository.emailmap_set.findIndex((e) => e.url == url);
                    if (index > -1) {
                        repository.emailmap_set.splice(index, 1);
                    }
                    resolve();
                })
                .catch((error) => {
                    reject(error.json());
                });
            }
        );
    }

    purgeAttachmentData(repository: Repository): Promise<any> {
        return new Promise((resolve, reject) => {
            this.http.post(repository.urls.purge_attachments, {}).toPromise()
                .then(() => resolve())
                .catch((error) => reject(error.json()));
            }
        );
    }

    fetchBasicInfo(uuid: string): Promise<Repository> {
        // URL path below is funky, just roll with it. Behind the scenes,
        // this POST also "approves" the repo if we're the right user.
        const url = `/api/github/repository/${uuid}/approve/`;
        return new Promise((resolve, reject) => {
            // If we happen to have this repo already, great.
            const respository = this.getByUuid(uuid);
            if (respository ) {
                resolve(respository);
            } else {
                this.http.post(url, {}).toPromise()
                    .then((response) => {
                        let repo = response.json() as Repository;
                        this.add(repo);
                        resolve(repo);
                    })
                    .catch((error) => reject(error.json()));
            }
        });
    }
}
