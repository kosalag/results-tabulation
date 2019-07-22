from config import db
from sqlalchemy.orm import relationship
from orm.enums import FileTypeEnum
import os
from orm.entities import FileCollection

FILE_DIRECTORY = os.path.join(os.getcwd(), 'data')


class Model(db.Model):
    __tablename__ = 'file'
    fileId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fileType = db.Column(db.Enum(FileTypeEnum), nullable=False)
    fileName = db.Column(db.String(100), nullable=True)
    fileMimeType = db.Column(db.String(100), nullable=False)
    fileContentLength = db.Column(db.String(100), nullable=False)
    fileContentType = db.Column(db.String(100), nullable=False)
    fileCollectionId = db.Column(db.Integer, db.ForeignKey(FileCollection.Model.__table__.c.fileCollectionId),
                                 nullable=True)

    __mapper_args__ = {
        'polymorphic_on': fileType,
        'polymorphic_identity': FileTypeEnum.Any
    }


FileCollection.files = relationship(Model)


def get_by_id(fileId):
    result = Model.query.filter(
        Model.fileId == fileId
    ).one_or_none()

    return result


def create(fileSource, fileType, fileCollectionId=None):
    # TODO validate the
    #   - file type
    #   - file size
    #         etc.

    result = Model(
        fileType=fileType,
        fileMimeType=fileSource.mimetype,
        fileContentLength=fileSource.content_length,
        fileContentType=fileSource.content_type,
        fileName=fileSource.filename,
        fileCollectionId=fileCollectionId
    )

    db.session.add(result)
    db.session.commit()

    save_file(result, fileSource)

    return result


def save_file(file, fileSource):
    file_path = os.path.join(FILE_DIRECTORY, str(file.fileId))

    fileSource.save(file_path)

    return file_path