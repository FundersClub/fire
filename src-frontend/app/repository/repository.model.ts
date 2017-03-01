import { EmailMap } from './email-map/email-map.model';

export class Repository {
    constructor(
        public email: string,
        public email_slug: string,
        public emailmap_set: Array<EmailMap>,
        public full_name: string, // `{login}/{name}`
        public login: string, // Owner of repo
        public name: string,
        public status: string, // "active", "pending-accept", "pending-inviter-approval"
        public url: string,
        public urls: {
            github: string,
            emailmap_add: string,
            purge_attachments: string
        }
    ) {}
}
