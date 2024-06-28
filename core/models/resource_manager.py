from mongoengine import Document, StringField, IntField

class ResourceManagerModel(Document):
    site = StringField(unique=True)
    component = StringField(unique=True)
    quantity = IntField()
    ttl = StringField() # maybe FloatField

    meta = {
        "db_alias": "tnlcm-database-alias",
        "collection": "resource_manager"
    }
            
    def to_dict(self):
        return {
            "site": self.site,
            "tn_id": self.tn_id,
            "component": self.component,
            "quantity": self.quantity,
            "ttl": self.ttl
        }

    def __repr__(self):
        return "<ResourceManager #%s: %s>" % (self.component, self.quantity)
    