from mongoengine import Document, StringField, IntField, ListField

class ResourceManagerModel(Document):
    site = StringField()
    tn_ids = ListField()
    component = StringField(default=[], unique=True)
    quantity = IntField()
    ttl = StringField() # maybe FloatField

    meta = {
        "db_alias": "tnlcm-database-alias",
        "collection": "resource_manager"
    }      
            
    def to_dict(self):
        return {
            "site": self.site,
            "tn_ids": self.tn_ids,
            "component": self.component,
            "quantity": self.quantity,
            "ttl": self.ttl
        }

    def __repr__(self):
        return "<ResourceManager #%s: %s>" % (self.component, self.quantity)
    