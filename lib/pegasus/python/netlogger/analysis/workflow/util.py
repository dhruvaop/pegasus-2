"""
Utility code to work with workflow databases.
"""

__rcsid__ = "$Id: util.py 28135 2011-07-05 20:07:28Z mgoode $"
__author__ = "Monte Goode"

from netlogger.analysis.schema.stampede_schema import *
from netlogger.analysis.modules._base import SQLAlchemyInit
from netlogger import util
from netlogger.nllog import DoesLogging

import os, time

class Expunge(SQLAlchemyInit, DoesLogging):
    """
    Utility class to expunge a workflow and the associated data from
    a stampede schema database in the case of running with the replay
    option or a similar situation.
    
    The wf_uuid that is passed into the constructor MUST be the 
    "top-level" workflow the user wants to delete.  Which is to
    say if the wf_uuid is a the child of another workflow, then
    only the data associated with that workflow will be deleted.  
    Any parent or sibling workflows will be left untouched.
    
    Usage::
     
     from netlogger.analysis.workflow.util import Expunge
     
     connString = 'sqlite:///pegasusMontage.db'
     wf_uuid = '1249335e-7692-4751-8da2-efcbb5024429'
     e = Expunge(connString, wf_uuid)
     e.expunge()
     
    All children/grand-children/etc information and associated
    workflows will be removed.
    """
    def __init__(self, connString, wf_uuid):
        """
        Init object
        
        @type   connString: string
        @param  connString: SQLAlchemy connection string - REQUIRED
        @type   wf_uuid: string
        @param  wf_uuid: The wf_uuid string of the workflow to remove
                along with associated data from the database
        """
        DoesLogging.__init__(self)
        self.log.info('init.start')
        SQLAlchemyInit.__init__(self, connString, initializeToPegasusDB)
        self._wf_uuid = wf_uuid
        self.log.info('init.end')
    
    def expunge(self):
        """
        Invoke this to remove workflow/information from DB.
        """
        self.log.info('expunge.start')
        self.session.autoflush=True
        # delete main workflow uuid and start cascade
        query = self.session.query(Workflow).filter(Workflow.wf_uuid == self._wf_uuid)
        try:
            wf = query.one()
        except orm.exc.NoResultFound, e:
            self.log.warn('expunge', msg='No workflow found with wf_uuid %s - aborting expunge' % self._wf_uuid)
            return
            
        root_wf_id = wf.wf_id
        
#        subs = []
        
#        query = self.session.query(Workflow.wf_id).filter(Workflow.root_wf_id == root_wf_id).filter(Workflow.wf_id != root_wf_id)
#        for row in query:
#            subs.append(row[0])
        
 #       for sub in subs:
 #           query = self.session.query(Workflow).filter(Workflow.wf_id == sub)
 #           subwf = query.one()
 #           self.log.info('expunge', msg='Expunging sub-workflow: %s' % subwf.wf_uuid)
 #           i = time.time()
 #           self.session.delete(subwf)
 #           self.session.flush()
 #           self.session.commit()
 #           self.log.info('expunge', msg='Flush took: %f seconds' % (time.time() - i))
            
        self.log.info('expunge', msg='Flushing top-level workflow: %s' % wf.wf_uuid)
        i = time.time()
        self.session.delete(wf)
        self.session.flush()
        self.session.commit()
        self.log.info('expunge', msg=' Flush took: %f seconds' % (time.time() - i) )
        # Disable autoflush
        self.session.autoflush=False
        pass

if __name__ == '__main__':
    pass
