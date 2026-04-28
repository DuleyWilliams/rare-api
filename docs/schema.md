# Rare — Database Schema

Ten models back the Rare platform, all defined under `rareapi/models/` and mapped to PostgreSQL through Django’s ORM. `RareUser` is the central model: it is the author of posts and comments, the source and target of subscriptions, and the user referenced in admin voting records. The fields shown for each model are only those declared in the local model file; inherited fields are noted separately below the diagram.

---

## ER Diagram

```mermaid
erDiagram

    RareUser {
        string bio
        string profile_image_url
        date created_on
    }

    Post {
        string title
        date publication_date
        string image_url
        text content
        bool approved
    }

    Category {
        string label
    }

    Tag {
        string label
    }

    PostTag {
    }

    Comment {
        string subject
        text content
        datetime created_on
    }

    Reaction {
        string label
        string image_url
    }

    PostReaction {
    }

    Subscription {
        date created_on
        datetime ended_on
    }

    DemotionQueue {
        string action
    }

    RareUser ||--o{ Post          : "user"
    Category ||--o{ Post          : "category"
    Post     ||--o{ PostTag       : "post"
    Tag      ||--o{ PostTag       : "tag"
    Post     ||--o{ Comment       : "post"
    RareUser ||--o{ Comment       : "author"
    Post     ||--o{ PostReaction  : "post"
    RareUser ||--o{ PostReaction  : "user"
    Reaction ||--o{ PostReaction  : "reaction"
    RareUser ||--o{ Subscription  : "follower"
    RareUser ||--o{ Subscription  : "author"
    RareUser ||--o{ DemotionQueue : "admin"
    RareUser ||--o{ DemotionQueue : "approver_one"