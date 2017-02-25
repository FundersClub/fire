import { EmailMap } from './email-map/email-map.model';

export class Repository {
    constructor(
        public emailmap_set: Array<EmailMap>,
        public email: string,
        public email_slug: string,
        public login: string, // Owner of repo
        public full_name: string, // `{login}/{name}`
        public gh_url: string,
        public name: string,
        public status: string, // "active", "pending-accept", "pending-inviter-approval"
        public url: string
    ) {}
}
