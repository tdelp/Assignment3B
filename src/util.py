import sys

def debugprint(*args, **kwargs):
    print(*args, file=sys.stderr, flush=True, **kwargs)

def pad_fields(docs):
    fields = set()
    for doc in docs:
        keys = doc.metadata.keys()
        types = [type(doc.metadata[key]) for key in keys]
        ktypes = list(zip(keys, types))
        fields.update(ktypes)
    for doc in docs:
        for field, ftype in fields:
            if field not in doc.metadata:
                doc.metadata[field] = ftype()

_GOOD_FIELD_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
def rename_fields(docs):
    fields = set()
    for doc in docs:
        keys = doc.metadata.keys()
        fields.update(keys)
    new_fields = {}
    for field in fields:
        new_name = field.replace(" ", "_")
        new_name = "".join(c if c in _GOOD_FIELD_CHARS else '_' for c in new_name)
        new_fields[field] = new_name
    for doc in docs:
        for field, new_name in new_fields.items():
            doc.metadata[new_name] = doc.metadata.pop(field)
    