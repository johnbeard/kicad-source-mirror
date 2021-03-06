/*
 * KiRouter - a push-and-(sometimes-)shove PCB router
 *
 * Copyright (C) 2013-2014 CERN
 * Author: Tomasz Wlostowski <tomasz.wlostowski@cern.ch>
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or (at your
 * option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef __PNS_ROUTING_SETTINGS
#define __PNS_ROUTING_SETTINGS

#include "direction.h"
#include "time_limit.h"
 
///> Routing modes
enum PNS_MODE
{
    RM_MarkObstacles = 0,   ///> Ignore collisions, mark obstacles
    RM_Shove,               ///> Only shove
    RM_Walkaround,          ///> Only walkaround
    RM_Smart                ///> Guess what's better, try to make least mess on the PCB
};

///> Optimization effort
enum PNS_OPTIMIZATION_EFFORT 
{
    OE_LOW = 0,             
    OE_MEDIUM = 1,
    OE_FULL = 2
};

/**
 * Class PNS_ROUTING_SETTINGS
 *
 * Contains all persistent settings of the router, such as the mode, optimization effort, etc.
 */

class PNS_ROUTING_SETTINGS
{
public:
    PNS_ROUTING_SETTINGS();

    ///> Returns the routing mode.
    PNS_MODE Mode() const { return m_routingMode; }

    ///> Sets the routing mode.
    void SetMode( PNS_MODE aMode ) { m_routingMode = aMode; }
    
    ///> Returns the optimizer effort. Bigger means cleaner traces, but slower routing.
    PNS_OPTIMIZATION_EFFORT OptimizerEffort() const { return m_optimizerEffort; }
    
    ///> Sets the optimizer effort. Bigger means cleaner traces, but slower routing.
    void SetOptimizerEffort( PNS_OPTIMIZATION_EFFORT aEffort ) { m_optimizerEffort = aEffort; }
    
    ///> Returns true if shoving vias is enbled.
    bool ShoveVias() const { return m_shoveVias; }

    ///> Enables/disables shoving vias.
    void SetShoveVias( bool aShoveVias ) { m_shoveVias = aShoveVias; }
    
    ///> Returns true if loop (redundant track) removal is on.
    bool RemoveLoops() const { return m_removeLoops; }

    ///> Enables/disables loop (redundant track) removal.
    void SetRemoveLoops( bool aRemoveLoops ) { m_removeLoops = aRemoveLoops; }
    
    ///> Returns true if suggesting the finish of currently placed track is on.
    bool SuggestFinish() { return m_suggestFinish; }
    
    ///> Enables displaying suggestions for finishing the currently placed track.
    void SetSuggestFinish( bool aSuggestFinish ) { m_suggestFinish = aSuggestFinish; }
    
    ///> Returns true if Smart Pads (automatic neckdown) is enabled.
    bool SmartPads () const { return m_smartPads; }

    ///> Enables/disables Smart Pads (automatic neckdown).
    void SetSmartPads( bool aSmartPads ) { m_smartPads = aSmartPads; }
    
    ///> Returns true if follow mouse mode is active (permanently on for the moment).
    bool FollowMouse() const 
    { 
        return m_followMouse && !( Mode() == RM_MarkObstacles );
    }
    
    ///> Returns true if smoothing segments durign dragging is enabled.    
    bool SmoothDraggedSegments() const { return m_smoothDraggedSegments; }

    ///> Enables/disabled smoothing segments during dragging.
    void SetSmoothDraggedSegments( bool aSmooth ) { m_smoothDraggedSegments = aSmooth; }

    ///> Returns true if jumping over unmovable obstacles is on.
    bool JumpOverObstacles() const { return m_jumpOverObstacles; }

    ///> Enables/disables jumping over unmovable obstacles.    
    void SetJumpOverObstacles( bool aJumpOverObstacles ) { m_jumpOverObstacles = aJumpOverObstacles; }
    
    void SetStartDiagonal(bool aStartDiagonal) { m_startDiagonal = aStartDiagonal; }
	
    bool CanViolateDRC() const { return m_canViolateDRC; }
    void SetCanViolateDRC( bool aViolate ) { m_canViolateDRC = aViolate; }

	void SetTrackWidth( int aWidth ) { m_trackWidth = aWidth; }
    int GetTrackWidth() const { return m_trackWidth; }
    void SetViaDiameter( int aDiameter ) { m_viaDiameter = aDiameter; }
    int GetViaDiameter() const { return m_viaDiameter; }
    void SetViaDrill( int aDrill ) { m_viaDrill = aDrill; }
    int GetViaDrill() const { return m_viaDrill; }

    const DIRECTION_45 InitialDirection() const
    {
        if( m_startDiagonal )
            return DIRECTION_45( DIRECTION_45::NE );
        else
            return DIRECTION_45( DIRECTION_45::N );
    }

    int ShoveIterationLimit() const;
    TIME_LIMIT ShoveTimeLimit() const;

    int WalkaroundIterationLimit() const { return m_walkaroundIterationLimit; };
    TIME_LIMIT WalkaroundTimeLimit() const;

private:
    bool m_shoveVias;
    bool m_startDiagonal;
    bool m_removeLoops;
    bool m_smartPads;
    bool m_suggestFinish;
    bool m_followMouse;
    bool m_jumpOverObstacles;
    bool m_smoothDraggedSegments;
    bool m_canViolateDRC;

    PNS_MODE m_routingMode;
    PNS_OPTIMIZATION_EFFORT m_optimizerEffort;
    
    int m_trackWidth;
    int m_viaDiameter;
    int m_viaDrill;

    int m_preferredLayer;
    int m_walkaroundIterationLimit;
    int m_shoveIterationLimit;
    TIME_LIMIT m_shoveTimeLimit;
    TIME_LIMIT m_walkaroundTimeLimit;
};

#endif
