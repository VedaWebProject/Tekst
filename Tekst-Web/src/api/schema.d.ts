export interface paths {
  '/bookmarks/{id}': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    post?: never;
    /** Delete bookmark */
    delete: operations['deleteBookmark'];
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/bookmarks': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Get user bookmarks
     * @description Returns all bookmarks that belong to the requesting user
     */
    get: operations['getUserBookmarks'];
    put?: never;
    /**
     * Create bookmark
     * @description Creates a bookmark for the requesting user
     */
    post: operations['createBookmark'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/browse/context': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Get content context
     * @description Returns a list of all resource contents belonging to the resource
     *     with the given ID, associated to locations that are children of the parent location
     *     with the given ID.
     */
    get: operations['getContentContext'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/browse': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Get location data
     * @description Returns the location path from the location with the given ID or text/level/position
     *     as the last element, up to its most distant ancestor location
     *     on structure level 0 as the first element of an array as well as all contents
     *     for the given resource(s) referencing the locations in the location path.
     */
    get: operations['getLocationData'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/browse/nearest-content-location': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Get nearest content location
     * @description Finds the nearest location the given resource holds content for and returns it.
     */
    get: operations['getNearestContentLocation'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/contents': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Find contents
     * @description Returns a list of all resource contents matching the given criteria.
     *
     *     Respects restricted resources and inactive texts.
     *     As the resulting list may contain contents of different types, the
     *     returned content objects cannot be typed to their precise resource content type.
     */
    get: operations['findContents'];
    put?: never;
    /** Create content */
    post: operations['createContent'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/contents/{id}': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Get content
     * @description A generic route for retrieving a content by ID from the database
     */
    get: operations['getContent'];
    put?: never;
    post?: never;
    /** Delete content */
    delete: operations['deleteContent'];
    options?: never;
    head?: never;
    /** Update content */
    patch: operations['updateContent'];
    trace?: never;
  };
  '/corrections': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /**
     * Create correction
     * @description Creates a correction note referring to a specific content
     */
    post: operations['createCorrection'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/corrections/{resourceId}': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Get corrections
     * @description Returns a list of all corrections for a specific resource
     */
    get: operations['getCorrections'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/corrections/{id}': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    post?: never;
    /**
     * Delete correction
     * @description Deletes a specific correction note
     */
    delete: operations['deleteCorrection'];
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/locations': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Find locations
     * @description Finds locations by various combinations of location properties.
     *     A full combined label including all parent location's labels is added to each
     *     returned location object if add_full_labels is set to true.
     */
    get: operations['findLocations'];
    put?: never;
    /**
     * Create location
     * @description Creates a new location. The position will be automatically set to the last position
     *     of the location's parent (or the first parent before that has children).
     */
    post: operations['createLocation'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/locations/{id}/path-options/{by}': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Get path options by head id
     * @description Returns the options for selecting text locations derived from the location path of
     *     the location with the given ID as head or root.
     */
    get: operations['getPathOptionsByHeadId'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/locations/first-last-paths': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Get first and last locations paths */
    get: operations['getFirstAndLastLocationsPaths'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/locations/children': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Get children */
    get: operations['getChildren'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/locations/{id}': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Get location */
    get: operations['getLocation'];
    put?: never;
    post?: never;
    /**
     * Delete location
     * @description Deletes the specified location. Also deletes any associated contents,
     *     child locations and contents associated with child locations.
     */
    delete: operations['deleteLocation'];
    options?: never;
    head?: never;
    /** Update location */
    patch: operations['updateLocation'];
    trace?: never;
  };
  '/locations/{id}/move': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /**
     * Move location
     * @description Moves the specified location to a new position on its level.
     */
    post: operations['moveLocation'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/messages': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Get thread messages
     * @description Returns all messages belonging to the specified thread
     */
    get: operations['getThreadMessages'];
    put?: never;
    /**
     * Send message
     * @description Creates a message for the specified recipient
     */
    post: operations['sendMessage'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/messages/threads': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Get threads
     * @description Returns all message threads involving the requesting user
     */
    get: operations['getThreads'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/messages/threads/{id}': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    post?: never;
    /**
     * Delete thread
     * @description Marks all received messages from the given user as deleted or actually deletes them,
     *     depending on the current deletion status
     */
    delete: operations['deleteThread'];
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/platform': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Get platform data
     * @description Returns data the client needs to initialize
     */
    get: operations['getPlatformData'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/platform/state': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    /** Update platform state */
    patch: operations['updatePlatformState'];
    trace?: never;
  };
  '/platform/segments/{id}': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Get segment */
    get: operations['getSegment'];
    put?: never;
    post?: never;
    /** Delete segment */
    delete: operations['deleteSegment'];
    options?: never;
    head?: never;
    /** Update segment */
    patch: operations['updateSegment'];
    trace?: never;
  };
  '/platform/segments': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Create segment */
    post: operations['createSegment'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/platform/tasks': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Get all tasks status */
    get: operations['getAllTasksStatus'];
    put?: never;
    post?: never;
    /** Delete all tasks */
    delete: operations['deleteAllTasks'];
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/platform/tasks/user': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Get user tasks */
    get: operations['getUserTasks'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/platform/tasks/download': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Download task artifact */
    get: operations['downloadTaskArtifact'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/platform/tasks/{id}': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    post?: never;
    /** Delete task */
    delete: operations['deleteTask'];
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/platform/cleanup': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Run platform cleanup */
    get: operations['runPlatformCleanup'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/resources/precompute': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Trigger resource precomputation */
    get: operations['triggerResourcePrecomputation'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/resources': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Find resources
     * @description Returns a list of all resources matching the given criteria.
     *
     *     As the resulting list of resources may contain resources of different types, the
     *     returned resource objects cannot be typed to their precise resource type.
     */
    get: operations['findResources'];
    put?: never;
    /** Create resource */
    post: operations['createResource'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/resources/{id}/version': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Create resource version */
    post: operations['createResourceVersion'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/resources/{id}': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Get resource */
    get: operations['getResource'];
    put?: never;
    post?: never;
    /** Delete resource */
    delete: operations['deleteResource'];
    options?: never;
    head?: never;
    /** Update resource */
    patch: operations['updateResource'];
    trace?: never;
  };
  '/resources/{id}/transfer': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Transfer resource */
    post: operations['transferResource'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/resources/{id}/propose': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Propose resource */
    post: operations['proposeResource'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/resources/{id}/unpropose': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Unpropose resource */
    post: operations['unproposeResource'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/resources/{id}/publish': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Publish resource */
    post: operations['publishResource'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/resources/{id}/unpublish': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Unpublish resource */
    post: operations['unpublishResource'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/resources/{id}/template': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Download resource template */
    get: operations['downloadResourceTemplate'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/resources/{id}/import': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Import resource contents */
    post: operations['importResourceContents'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/resources/{id}/export': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Export resource contents */
    get: operations['exportResourceContents'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/resources/{id}/aggregations': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Get annotation aggregations */
    get: operations['getAnnotationAggregations'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/resources/{id}/coverage': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Get resource coverage data */
    get: operations['getResourceCoverageData'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/search': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Perform search */
    post: operations['performSearch'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/search/index/create': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Create search index */
    get: operations['createSearchIndex'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/search/index/info': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Get search index info */
    get: operations['getSearchIndexInfo'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/search/export': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Export search results */
    post: operations['exportSearchResults'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/status': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Api status */
    get: operations['apiStatus'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/texts': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Get all texts
     * @description Returns a list of all texts.
     *     Only users with admin permissions will see inactive texts.
     */
    get: operations['getAllTexts'];
    put?: never;
    /** Create text */
    post: operations['createText'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/texts/{id}/template': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Download structure template
     * @description Download the structure template for a text to help compose a structure
     *     definition (or locations updates if there already is a structure)
     *     that can later be uploaded to the server.
     */
    get: operations['downloadStructureTemplate'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/texts/{id}/structure': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /**
     * Import text structure
     * @description Uploads the structure definition for a text to apply as a structure of locations
     */
    post: operations['importTextStructure'];
    delete?: never;
    options?: never;
    head?: never;
    /**
     * Update text structure
     * @description Uploads updated locations data.
     *     Only existing locations (with a correct ID) will be updated.
     */
    patch: operations['updateTextStructure'];
    trace?: never;
  };
  '/texts/{id}/level/{index}': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Insert level */
    post: operations['insertLevel'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/texts/{id}/level/{lvl}': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    post?: never;
    /** Delete level */
    delete: operations['deleteLevel'];
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/texts/{id}': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Get text */
    get: operations['getText'];
    put?: never;
    post?: never;
    /** Delete text */
    delete: operations['deleteText'];
    options?: never;
    head?: never;
    /** Update text */
    patch: operations['updateText'];
    trace?: never;
  };
  '/users/me': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Me */
    get: operations['users:currentUser'];
    put?: never;
    post?: never;
    /** Delete me */
    delete: operations['deleteMe'];
    options?: never;
    head?: never;
    /** Update me */
    patch: operations['users:patchCurrentUser'];
    trace?: never;
  };
  '/users': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Find users */
    get: operations['findUsers'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/users/public/{user}': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Get public user
     * @description Returns public information on the user with the specified username or ID
     */
    get: operations['getPublicUser'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/users/public': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Find public users
     * @description Returns a list of public users matching the given query.
     *
     *     Only returns active user accounts. The query is considered to match a full token
     *     (e.g. first name, last name, username, a word in the affiliation field).
     */
    get: operations['findPublicUsers'];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/auth/cookie/login': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Login */
    post: operations['auth:cookie.login'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/auth/cookie/logout': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Logout */
    post: operations['auth:cookie.logout'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/auth/register': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Register */
    post: operations['register:register'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/auth/request-verify-token': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Request verify token */
    post: operations['verify:requestToken'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/auth/verify': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Verify */
    post: operations['verify:verify'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/auth/forgot-password': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Forgot password */
    post: operations['reset:forgotPassword'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/auth/reset-password': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Reset password */
    post: operations['reset:resetPassword'];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  '/users/{id}': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Get user */
    get: operations['users:user'];
    put?: never;
    post?: never;
    /** Delete user */
    delete: operations['users:deleteUser'];
    options?: never;
    head?: never;
    /** Update user */
    patch: operations['users:patchUser'];
    trace?: never;
  };
}
export type webhooks = Record<string, never>;
export interface components {
  schemas: {
    /** @enum {string} */
    AdminNotificationTrigger: 'userAwaitsActivation' | 'newCorrection';
    /** AdvancedSearchRequestBody */
    AdvancedSearchRequestBody: {
      /**
       * @description Search type (enum property replaced by openapi-typescript)
       * @enum {string}
       */
      type: 'advanced';
      /**
       * Q
       * @description Resource-specific queries
       * @default []
       */
      q?: components['schemas']['ResourceSearchQuery'][];
      /**
       * @description General search settings
       * @default {
       *       "pgn": {
       *         "pg": 1,
       *         "pgs": 10
       *       },
       *       "strict": false
       *     }
       */
      gen?: components['schemas']['GeneralSearchSettings'];
      /**
       * @description Advanced search settings
       * @default {}
       */
      adv?: components['schemas']['AdvancedSearchSettings'];
    };
    /** AdvancedSearchSettings */
    AdvancedSearchSettings: Record<string, never>;
    /** AnnotationAggregation */
    AnnotationAggregation: {
      /** Key */
      key: string;
      /** Values */
      values?: string[] | null;
    };
    /** AnnotationGroup */
    AnnotationGroup: {
      /**
       * Key
       * @description Key identifying this annotation group
       */
      key: string;
      /**
       * Translations
       * @description Translation for the label of an annotation group
       */
      translations: components['schemas']['AnnotationGroupTranslation'][];
    };
    /** AnnotationGroupTranslation */
    AnnotationGroupTranslation: {
      locale: components['schemas']['TranslationLocaleKey'];
      /**
       * Translation
       * @description Translation of an annotation group label
       */
      translation: string;
    };
    /** ApiCallContentCreate */
    ApiCallContentCreate: {
      /**
       * Resourceid
       * @description Resource ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      resourceId: string;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'apiCall';
      /**
       * Locationid
       * @description Text location ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      locationId: string;
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: null | string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: null | string;
      /**
       * Query
       * @description Query payload to use for the API call. This can be a URL query string,(for GET requests) a JSON object, or whatever the API expects.
       */
      query: string;
      /**
       * Transformcontext
       * @description Extra data that will be made available to the transformation script. This has to be a valid, string-encoded JSON object.
       */
      transformContext?: string;
    };
    /** ApiCallContentRead */
    ApiCallContentRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Resourceid
       * @description Resource ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      resourceId: string;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'apiCall';
      /**
       * Locationid
       * @description Text location ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      locationId: string;
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: null | string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: null | string;
      /**
       * Query
       * @description Query payload to use for the API call. This can be a URL query string,(for GET requests) a JSON object, or whatever the API expects.
       */
      query: string;
      /**
       * Transformcontext
       * @description Extra data that will be made available to the transformation script. This has to be a valid, string-encoded JSON object.
       */
      transformContext?: string;
    } & {
      [key: string]: unknown;
    };
    /** ApiCallContentUpdate */
    ApiCallContentUpdate: {
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'apiCall';
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: string;
      /**
       * Query
       * @description Query payload to use for the API call. This can be a URL query string,(for GET requests) a JSON object, or whatever the API expects.
       */
      query?: string;
      /**
       * Transformcontext
       * @description Extra data that will be made available to the transformation script. This has to be a valid, string-encoded JSON object.
       */
      transformContext?: string;
    };
    /** ApiCallModifiedCommonResourceConfig */
    ApiCallModifiedCommonResourceConfig: {
      /**
       * Category
       * @description Resource category key
       */
      category?: null | string;
      /**
       * Sortorder
       * @description Sort order for displaying this resource among others
       * @default 10
       */
      sortOrder: number;
      /**
       * Defaultactive
       * @description Whether this resource is active by default when public
       * @default true
       */
      defaultActive?: boolean;
      /**
       * Enablecontentcontext
       * @description Whether contents of this resource should be available for the parent level (always false for API call resources)
       * @default false
       * @constant
       */
      enableContentContext?: false;
      /**
       * Searchablequick
       * @description Whether this resource should be included in quick search (always false as API call contents are not searchable)
       * @default false
       * @constant
       */
      searchableQuick?: false;
      /**
       * Searchableadv
       * @description Whether this resource should accessible via advanced search (always false as API call contents are not searchable)
       * @default false
       * @constant
       */
      searchableAdv?: false;
      /**
       * Rtl
       * @description Whether to display text contents in right-to-left direction
       * @default false
       */
      rtl?: boolean;
      /** Osk */
      osk?: string | null;
    };
    /** ApiCallResourceConfig */
    ApiCallResourceConfig: {
      /** @default {
       *       "sortOrder": 10,
       *       "defaultActive": true,
       *       "enableContentContext": false,
       *       "searchableQuick": false,
       *       "searchableAdv": false,
       *       "rtl": false
       *     } */
      common: components['schemas']['ApiCallModifiedCommonResourceConfig'];
      /** @default {
       *       "defaultCollapsed": false
       *     } */
      general: components['schemas']['GeneralApiCallResourceConfig'];
      /** @default {
       *       "endpoint": "https://api.example.com/v2/some/endpoint",
       *       "method": "GET",
       *       "contentType": "application/json",
       *       "transformDeps": []
       *     } */
      apiCall: components['schemas']['ApiCallSpecialConfig'];
    };
    /** ApiCallResourceCreate */
    ApiCallResourceCreate: {
      /**
       * Title
       * @description Title of this resource
       */
      title: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       * @default []
       */
      description: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * Textid
       * @description ID of the text this resource belongs to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      textId: string;
      /**
       * Level
       * @description Text level this resource belongs to
       */
      level: number;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'apiCall';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: null | string;
      /**
       * Meta
       * @description Arbitrary metadata
       * @default []
       */
      meta: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       * @default []
       */
      comment: components['schemas']['ResourceCommentTranslation'][];
      /** @default {
       *       "common": {
       *         "defaultActive": true,
       *         "enableContentContext": false,
       *         "rtl": false,
       *         "searchableAdv": false,
       *         "searchableQuick": false,
       *         "sortOrder": 10
       *       },
       *       "general": {
       *         "defaultCollapsed": false
       *       },
       *       "apiCall": {
       *         "contentType": "application/json",
       *         "endpoint": "https://api.example.com/v2/some/endpoint",
       *         "method": "GET",
       *         "transformDeps": []
       *       }
       *     } */
      config: components['schemas']['ApiCallResourceConfig'];
    };
    /** ApiCallResourceRead */
    ApiCallResourceRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Writable
       * @description Whether this resource is writable for the requesting user
       */
      writable?: boolean | null;
      /** @description Public user data for user owning this resource */
      owner?: components['schemas']['UserReadPublic'] | null;
      /**
       * Sharedreadusers
       * @description Public user data for users allowed to read this resource
       */
      sharedReadUsers?: components['schemas']['UserReadPublic'][] | null;
      /**
       * Sharedwriteusers
       * @description Public user data for users allowed to write this resource
       */
      sharedWriteUsers?: components['schemas']['UserReadPublic'][] | null;
      /**
       * Title
       * @description Title of this resource
       */
      title: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       * @default []
       */
      description: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * Textid
       * @description ID of the text this resource belongs to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      textId: string;
      /**
       * Level
       * @description Text level this resource belongs to
       */
      level: number;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'apiCall';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Ownerid
       * @description User owning this resource
       */
      ownerId?: string | null;
      /**
       * Sharedread
       * @description Users with shared read access to this resource
       * @default []
       */
      sharedRead: string[];
      /**
       * Sharedwrite
       * @description Users with shared write access to this resource
       * @default []
       */
      sharedWrite: string[];
      /**
       * Public
       * @description Publication status of this resource
       * @default false
       */
      public: boolean;
      /**
       * Proposed
       * @description Whether this resource has been proposed for publication
       * @default false
       */
      proposed: boolean;
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: null | string;
      /**
       * Meta
       * @description Arbitrary metadata
       * @default []
       */
      meta: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       * @default []
       */
      comment: components['schemas']['ResourceCommentTranslation'][];
      /** @default {
       *       "common": {
       *         "defaultActive": true,
       *         "enableContentContext": false,
       *         "rtl": false,
       *         "searchableAdv": false,
       *         "searchableQuick": false,
       *         "sortOrder": 10
       *       },
       *       "general": {
       *         "defaultCollapsed": false
       *       },
       *       "apiCall": {
       *         "contentType": "application/json",
       *         "endpoint": "https://api.example.com/v2/some/endpoint",
       *         "method": "GET",
       *         "transformDeps": []
       *       }
       *     } */
      config: components['schemas']['ApiCallResourceConfig'];
      /**
       * Contentschangedat
       * Format: date-time
       * @description The last time contents of this resource changed
       * @default 1970-01-02T00:00:00
       */
      contentsChangedAt: string;
    } & {
      [key: string]: unknown;
    };
    /** ApiCallResourceUpdate */
    ApiCallResourceUpdate: {
      /**
       * Title
       * @description Title of this resource
       */
      title?: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       */
      description?: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'apiCall';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Sharedread
       * @description Users with shared read access to this resource
       */
      sharedRead?: string[];
      /**
       * Sharedwrite
       * @description Users with shared write access to this resource
       */
      sharedWrite?: string[];
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: string;
      /**
       * Meta
       * @description Arbitrary metadata
       */
      meta?: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       */
      comment?: components['schemas']['ResourceCommentTranslation'][];
      config?: components['schemas']['ApiCallResourceConfig'];
    };
    /**
     * ApiCallSpecialConfig
     * @description Config properties specific to the API call resource type
     */
    ApiCallSpecialConfig: {
      /**
       * Endpoint
       * @default https://api.example.com/v2/some/endpoint
       */
      endpoint: string;
      /**
       * Method
       * @default GET
       * @enum {string}
       */
      method: 'GET' | 'POST' | 'QUERY' | 'SEARCH';
      /**
       * Contenttype
       * @default application/json
       */
      contentType: string;
      /**
       * Transformdeps
       * @default []
       */
      transformDeps: string[];
      /** Transformjs */
      transformJs?: string;
    };
    /** AudioContentCreate */
    AudioContentCreate: {
      /**
       * Resourceid
       * @description Resource ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      resourceId: string;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'audio';
      /**
       * Locationid
       * @description Text location ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      locationId: string;
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: null | string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: null | string;
      /**
       * Files
       * @description List of audio file objects
       */
      files: components['schemas']['AudioFile'][];
    };
    /** AudioContentRead */
    AudioContentRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Resourceid
       * @description Resource ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      resourceId: string;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'audio';
      /**
       * Locationid
       * @description Text location ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      locationId: string;
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: null | string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: null | string;
      /**
       * Files
       * @description List of audio file objects
       */
      files: components['schemas']['AudioFile'][];
    } & {
      [key: string]: unknown;
    };
    /** AudioContentUpdate */
    AudioContentUpdate: {
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'audio';
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: string;
      /**
       * Files
       * @description List of audio file objects
       */
      files?: components['schemas']['AudioFile'][];
    };
    /** AudioFile */
    AudioFile: {
      /**
       * Url
       * @description URL of the audio file
       */
      url: string;
      /**
       * Sourceurl
       * @description URL of the source website of the image
       */
      sourceUrl?: null | string;
      /**
       * Caption
       * @description Caption of the audio file
       */
      caption?: null | string;
    };
    /** AudioResourceConfig */
    AudioResourceConfig: {
      /** @default {
       *       "sortOrder": 10,
       *       "defaultActive": true,
       *       "enableContentContext": false,
       *       "searchableQuick": true,
       *       "searchableAdv": true,
       *       "rtl": false
       *     } */
      common: components['schemas']['CommonResourceConfig'];
      /** @default {
       *       "defaultCollapsed": false
       *     } */
      general: components['schemas']['GeneralAudioResourceConfig'];
    };
    /** AudioResourceCreate */
    AudioResourceCreate: {
      /**
       * Title
       * @description Title of this resource
       */
      title: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       * @default []
       */
      description: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * Textid
       * @description ID of the text this resource belongs to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      textId: string;
      /**
       * Level
       * @description Text level this resource belongs to
       */
      level: number;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'audio';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: null | string;
      /**
       * Meta
       * @description Arbitrary metadata
       * @default []
       */
      meta: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       * @default []
       */
      comment: components['schemas']['ResourceCommentTranslation'][];
      /** @default {
       *       "common": {
       *         "defaultActive": true,
       *         "enableContentContext": false,
       *         "rtl": false,
       *         "searchableAdv": true,
       *         "searchableQuick": true,
       *         "sortOrder": 10
       *       },
       *       "general": {
       *         "defaultCollapsed": false
       *       }
       *     } */
      config: components['schemas']['AudioResourceConfig'];
    };
    /** AudioResourceRead */
    AudioResourceRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Writable
       * @description Whether this resource is writable for the requesting user
       */
      writable?: boolean | null;
      /** @description Public user data for user owning this resource */
      owner?: components['schemas']['UserReadPublic'] | null;
      /**
       * Sharedreadusers
       * @description Public user data for users allowed to read this resource
       */
      sharedReadUsers?: components['schemas']['UserReadPublic'][] | null;
      /**
       * Sharedwriteusers
       * @description Public user data for users allowed to write this resource
       */
      sharedWriteUsers?: components['schemas']['UserReadPublic'][] | null;
      /**
       * Title
       * @description Title of this resource
       */
      title: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       * @default []
       */
      description: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * Textid
       * @description ID of the text this resource belongs to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      textId: string;
      /**
       * Level
       * @description Text level this resource belongs to
       */
      level: number;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'audio';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Ownerid
       * @description User owning this resource
       */
      ownerId?: string | null;
      /**
       * Sharedread
       * @description Users with shared read access to this resource
       * @default []
       */
      sharedRead: string[];
      /**
       * Sharedwrite
       * @description Users with shared write access to this resource
       * @default []
       */
      sharedWrite: string[];
      /**
       * Public
       * @description Publication status of this resource
       * @default false
       */
      public: boolean;
      /**
       * Proposed
       * @description Whether this resource has been proposed for publication
       * @default false
       */
      proposed: boolean;
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: null | string;
      /**
       * Meta
       * @description Arbitrary metadata
       * @default []
       */
      meta: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       * @default []
       */
      comment: components['schemas']['ResourceCommentTranslation'][];
      /** @default {
       *       "common": {
       *         "defaultActive": true,
       *         "enableContentContext": false,
       *         "rtl": false,
       *         "searchableAdv": true,
       *         "searchableQuick": true,
       *         "sortOrder": 10
       *       },
       *       "general": {
       *         "defaultCollapsed": false
       *       }
       *     } */
      config: components['schemas']['AudioResourceConfig'];
      /**
       * Contentschangedat
       * Format: date-time
       * @description The last time contents of this resource changed
       * @default 1970-01-02T00:00:00
       */
      contentsChangedAt: string;
    } & {
      [key: string]: unknown;
    };
    /** AudioResourceUpdate */
    AudioResourceUpdate: {
      /**
       * Title
       * @description Title of this resource
       */
      title?: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       */
      description?: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'audio';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Sharedread
       * @description Users with shared read access to this resource
       */
      sharedRead?: string[];
      /**
       * Sharedwrite
       * @description Users with shared write access to this resource
       */
      sharedWrite?: string[];
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: string;
      /**
       * Meta
       * @description Arbitrary metadata
       */
      meta?: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       */
      comment?: components['schemas']['ResourceCommentTranslation'][];
      config?: components['schemas']['AudioResourceConfig'];
    };
    /** AudioSearchQuery */
    AudioSearchQuery: {
      /**
       * @description Type of the resource to search in (enum property replaced by openapi-typescript)
       * @enum {string}
       */
      type: 'audio';
      /**
       * Caption
       * @default
       */
      caption?: string;
    };
    /** Body_auth_cookie_login_auth_cookie_login_post */
    Body_auth_cookie_login_auth_cookie_login_post: {
      /** Grant Type */
      grant_type?: string | null;
      /** Username */
      username: string;
      /** Password */
      password: string;
      /**
       * Scope
       * @default
       */
      scope: string;
      /** Client Id */
      client_id?: string | null;
      /** Client Secret */
      client_secret?: string | null;
    };
    /** Body_import_resource_contents_resources__id__import_post */
    Body_import_resource_contents_resources__id__import_post: {
      /**
       * File
       * Format: binary
       * @description JSON file containing the resource content data
       */
      file: Blob;
    };
    /** Body_import_text_structure_texts__id__structure_post */
    Body_import_text_structure_texts__id__structure_post: {
      /**
       * File
       * Format: binary
       * @description JSON file containing the text's structure
       */
      file: Blob;
    };
    /** Body_reset_forgot_password_auth_forgot_password_post */
    Body_reset_forgot_password_auth_forgot_password_post: {
      /**
       * Email
       * Format: email
       */
      email: string;
    };
    /** Body_reset_reset_password_auth_reset_password_post */
    Body_reset_reset_password_auth_reset_password_post: {
      /** Token */
      token: string;
      /** Password */
      password: string;
    };
    /** Body_update_text_structure_texts__id__structure_patch */
    Body_update_text_structure_texts__id__structure_patch: {
      /**
       * File
       * Format: binary
       * @description JSON file containing the locations to update
       */
      file: Blob;
    };
    /** Body_verify_request_token_auth_request_verify_token_post */
    Body_verify_request_token_auth_request_verify_token_post: {
      /**
       * Email
       * Format: email
       */
      email: string;
    };
    /** Body_verify_verify_auth_verify_post */
    Body_verify_verify_auth_verify_post: {
      /** Token */
      token: string;
    };
    /** BookmarkCreate */
    BookmarkCreate: {
      /**
       * Locationid
       * @description ID of the text location this bookmark refers to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      locationId: string;
      /**
       * Comment
       * @description Comment associated with this bookmark
       */
      comment?: null | string;
    };
    /** BookmarkRead */
    BookmarkRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Userid
       * @description ID of user who created this bookmark
       * @example 5eb7cf5a86d9755df3a6c593
       */
      userId: string;
      /**
       * Textid
       * @description ID of text this bookmark belongs to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      textId: string;
      /**
       * Locationid
       * @description ID of the text location this bookmark refers to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      locationId: string;
      /**
       * Level
       * @description Text level this bookmark refers to
       */
      level: number;
      /**
       * Position
       * @description Position of the text location this bookmark refers to
       */
      position: number;
      /**
       * Locationlabels
       * @description Text location labels from root to target location
       */
      locationLabels: string[];
      /**
       * Comment
       * @description Comment associated with this bookmark
       */
      comment?: null | string;
    } & {
      [key: string]: unknown;
    };
    /** ClientSegmentCreate */
    ClientSegmentCreate: {
      /**
       * Key
       * @description Key of this segment. System segment keys must start with `system`.
       */
      key: string;
      /**
       * Editormode
       * @description Last used editor mode
       * @default wysiwyg
       * @enum {string}
       */
      editorMode: 'wysiwyg' | 'html';
      /** @description Locale indicating the translation language of this segment */
      locale: components['schemas']['TranslationLocaleKey'];
      /**
       * Title
       * @description Title of this segment
       */
      title: string;
      /**
       * Html
       * @description HTML content of this segment
       */
      html: string;
    };
    /** ClientSegmentHead */
    ClientSegmentHead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /** Key */
      key: string;
      /** Title */
      title?: string | null;
      locale: components['schemas']['TranslationLocaleKey'];
    };
    /** ClientSegmentRead */
    ClientSegmentRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Key
       * @description Key of this segment. System segment keys must start with `system`.
       */
      key: string;
      /**
       * Editormode
       * @description Last used editor mode
       * @default wysiwyg
       * @enum {string}
       */
      editorMode: 'wysiwyg' | 'html';
      /** @description Locale indicating the translation language of this segment */
      locale: components['schemas']['TranslationLocaleKey'];
      /**
       * Title
       * @description Title of this segment
       */
      title: string;
      /**
       * Html
       * @description HTML content of this segment
       */
      html: string;
    } & {
      [key: string]: unknown;
    };
    /** ClientSegmentUpdate */
    ClientSegmentUpdate: {
      /**
       * Key
       * @description Key of this segment. System segment keys must start with `system`.
       */
      key?: string;
      /**
       * Editormode
       * @description Last used editor mode
       */
      editorMode?: 'wysiwyg' | 'html';
      /** @description Locale indicating the translation language of this segment */
      locale?: components['schemas']['TranslationLocaleKey'];
      /**
       * Title
       * @description Title of this segment
       */
      title?: string;
      /**
       * Html
       * @description HTML content of this segment
       */
      html?: string;
    };
    /** CommonResourceConfig */
    CommonResourceConfig: {
      /**
       * Category
       * @description Resource category key
       */
      category?: null | string;
      /**
       * Sortorder
       * @description Sort order for displaying this resource among others
       * @default 10
       */
      sortOrder: number;
      /**
       * Defaultactive
       * @description Whether this resource is active by default when public
       * @default true
       */
      defaultActive?: boolean;
      /**
       * Enablecontentcontext
       * @description Show combined contents of this resource on the parent level
       * @default false
       */
      enableContentContext?: boolean;
      /**
       * Searchablequick
       * @description Whether this resource should be included in quick search
       * @default true
       */
      searchableQuick?: boolean;
      /**
       * Searchableadv
       * @description Whether this resource should accessible via advanced search
       * @default true
       */
      searchableAdv?: boolean;
      /**
       * Rtl
       * @description Whether to display text contents in right-to-left direction
       * @default false
       */
      rtl?: boolean;
      /** Osk */
      osk?: string | null;
    };
    /** CommonResourceSearchQueryData */
    CommonResourceSearchQueryData: {
      /**
       * Occ
       * @description The occurrence type of the search query
       * @default must
       * @enum {string}
       */
      occ?: 'should' | 'must' | 'not';
      /**
       * Res
       * @description ID of the resource to search in
       * @example 5eb7cf5a86d9755df3a6c593
       */
      res: string;
      /**
       * Cmt
       * @description Comment search query
       * @default
       */
      cmt?: string;
    };
    ContentCssProperties: components['schemas']['ContentCssProperty'][];
    /** ContentCssProperty */
    ContentCssProperty: {
      /**
       * Prop
       * @description A CSS property name
       */
      prop: string;
      /**
       * Value
       * @description A CSS property value
       */
      value: string;
    };
    /** CorrectionCreate */
    CorrectionCreate: {
      /**
       * Resourceid
       * @description ID of the resource this correction refers to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      resourceId: string;
      /**
       * Locationid
       * @description ID of the location this correction refers to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      locationId: string;
      /**
       * Note
       * @description Content of the correction note
       */
      note: string;
    };
    /** CorrectionRead */
    CorrectionRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Resourceid
       * @description ID of the resource this correction refers to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      resourceId: string;
      /**
       * Locationid
       * @description ID of the location this correction refers to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      locationId: string;
      /**
       * Note
       * @description Content of the correction note
       */
      note: string;
      /**
       * Userid
       * @description ID of the user who created the correction note
       * @example 5eb7cf5a86d9755df3a6c593
       */
      userId: string;
      /**
       * Position
       * @description Position of the correction on the resource's level
       */
      position: number;
      /**
       * Date
       * Format: date-time
       * @description Date when the correction was created
       */
      date: string;
      /**
       * Locationlabels
       * @description Text location labels from root to target location
       */
      locationLabels: string[];
    } & {
      [key: string]: unknown;
    };
    /**
     * DeepLLinksConfig
     * @description Resource configuration model for DeepL translation links.
     *     The corresponding field MUST be named `deepl_links`!
     */
    DeepLLinksConfig: {
      /**
       * Enabled
       * @description Enable/disable quick translation links to DeepL
       * @default false
       */
      enabled: boolean;
      /** @description Source language */
      sourceLanguage?: components['schemas']['DeepLSourceLanguage'] | null;
    };
    /** @enum {string} */
    DeepLSourceLanguage:
      | 'ar'
      | 'bg'
      | 'cs'
      | 'da'
      | 'de'
      | 'el'
      | 'en'
      | 'es'
      | 'et'
      | 'fi'
      | 'fr'
      | 'hu'
      | 'id'
      | 'it'
      | 'ja'
      | 'ko'
      | 'lt'
      | 'lv'
      | 'nb'
      | 'nl'
      | 'pl'
      | 'pt'
      | 'ro'
      | 'ru'
      | 'sk'
      | 'sl'
      | 'sv'
      | 'tr'
      | 'uk'
      | 'zh';
    /** DeleteLocationResult */
    DeleteLocationResult: {
      /** Contents */
      contents: number;
      /** Locations */
      locations: number;
    };
    /** ErrorDetail */
    ErrorDetail: {
      /** Key */
      key: string;
      /** Msg */
      msg?: null | string;
      /** Values */
      values?: {
        [key: string]: string | number | boolean;
      } | null;
    };
    /** ErrorModel */
    ErrorModel: {
      /** Detail */
      detail:
        | string
        | {
            [key: string]: string;
          };
    };
    /** ExternalReferencesContentCreate */
    ExternalReferencesContentCreate: {
      /**
       * Resourceid
       * @description Resource ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      resourceId: string;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'externalReferences';
      /**
       * Locationid
       * @description Text location ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      locationId: string;
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: null | string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: null | string;
      /**
       * Links
       * @description List of external reference link objects
       */
      links: components['schemas']['ExternalReferencesLink'][];
    };
    /** ExternalReferencesContentRead */
    ExternalReferencesContentRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Resourceid
       * @description Resource ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      resourceId: string;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'externalReferences';
      /**
       * Locationid
       * @description Text location ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      locationId: string;
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: null | string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: null | string;
      /**
       * Links
       * @description List of external reference link objects
       */
      links: components['schemas']['ExternalReferencesLink'][];
    } & {
      [key: string]: unknown;
    };
    /** ExternalReferencesContentUpdate */
    ExternalReferencesContentUpdate: {
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'externalReferences';
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: string;
      /**
       * Links
       * @description List of external reference link objects
       */
      links?: components['schemas']['ExternalReferencesLink'][];
    };
    /** ExternalReferencesLink */
    ExternalReferencesLink: {
      /**
       * Url
       * @description URL of the link
       */
      url: string;
      /**
       * Title
       * @description Title/text of the link
       */
      title: string;
      /**
       * Description
       * @description Description of the link
       */
      description?: string;
    };
    /** ExternalReferencesResourceConfig */
    ExternalReferencesResourceConfig: {
      /** @default {
       *       "sortOrder": 10,
       *       "defaultActive": true,
       *       "enableContentContext": false,
       *       "searchableQuick": true,
       *       "searchableAdv": true,
       *       "rtl": false
       *     } */
      common: components['schemas']['CommonResourceConfig'];
      /** @default {
       *       "defaultCollapsed": false
       *     } */
      general: components['schemas']['GeneralExternalReferencesResourceConfig'];
    };
    /** ExternalReferencesResourceCreate */
    ExternalReferencesResourceCreate: {
      /**
       * Title
       * @description Title of this resource
       */
      title: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       * @default []
       */
      description: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * Textid
       * @description ID of the text this resource belongs to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      textId: string;
      /**
       * Level
       * @description Text level this resource belongs to
       */
      level: number;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'externalReferences';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: null | string;
      /**
       * Meta
       * @description Arbitrary metadata
       * @default []
       */
      meta: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       * @default []
       */
      comment: components['schemas']['ResourceCommentTranslation'][];
      /** @default {
       *       "common": {
       *         "defaultActive": true,
       *         "enableContentContext": false,
       *         "rtl": false,
       *         "searchableAdv": true,
       *         "searchableQuick": true,
       *         "sortOrder": 10
       *       },
       *       "general": {
       *         "defaultCollapsed": false
       *       }
       *     } */
      config: components['schemas']['ExternalReferencesResourceConfig'];
    };
    /** ExternalReferencesResourceRead */
    ExternalReferencesResourceRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Writable
       * @description Whether this resource is writable for the requesting user
       */
      writable?: boolean | null;
      /** @description Public user data for user owning this resource */
      owner?: components['schemas']['UserReadPublic'] | null;
      /**
       * Sharedreadusers
       * @description Public user data for users allowed to read this resource
       */
      sharedReadUsers?: components['schemas']['UserReadPublic'][] | null;
      /**
       * Sharedwriteusers
       * @description Public user data for users allowed to write this resource
       */
      sharedWriteUsers?: components['schemas']['UserReadPublic'][] | null;
      /**
       * Title
       * @description Title of this resource
       */
      title: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       * @default []
       */
      description: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * Textid
       * @description ID of the text this resource belongs to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      textId: string;
      /**
       * Level
       * @description Text level this resource belongs to
       */
      level: number;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'externalReferences';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Ownerid
       * @description User owning this resource
       */
      ownerId?: string | null;
      /**
       * Sharedread
       * @description Users with shared read access to this resource
       * @default []
       */
      sharedRead: string[];
      /**
       * Sharedwrite
       * @description Users with shared write access to this resource
       * @default []
       */
      sharedWrite: string[];
      /**
       * Public
       * @description Publication status of this resource
       * @default false
       */
      public: boolean;
      /**
       * Proposed
       * @description Whether this resource has been proposed for publication
       * @default false
       */
      proposed: boolean;
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: null | string;
      /**
       * Meta
       * @description Arbitrary metadata
       * @default []
       */
      meta: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       * @default []
       */
      comment: components['schemas']['ResourceCommentTranslation'][];
      /** @default {
       *       "common": {
       *         "defaultActive": true,
       *         "enableContentContext": false,
       *         "rtl": false,
       *         "searchableAdv": true,
       *         "searchableQuick": true,
       *         "sortOrder": 10
       *       },
       *       "general": {
       *         "defaultCollapsed": false
       *       }
       *     } */
      config: components['schemas']['ExternalReferencesResourceConfig'];
      /**
       * Contentschangedat
       * Format: date-time
       * @description The last time contents of this resource changed
       * @default 1970-01-02T00:00:00
       */
      contentsChangedAt: string;
    } & {
      [key: string]: unknown;
    };
    /** ExternalReferencesResourceUpdate */
    ExternalReferencesResourceUpdate: {
      /**
       * Title
       * @description Title of this resource
       */
      title?: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       */
      description?: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'externalReferences';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Sharedread
       * @description Users with shared read access to this resource
       */
      sharedRead?: string[];
      /**
       * Sharedwrite
       * @description Users with shared write access to this resource
       */
      sharedWrite?: string[];
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: string;
      /**
       * Meta
       * @description Arbitrary metadata
       */
      meta?: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       */
      comment?: components['schemas']['ResourceCommentTranslation'][];
      config?: components['schemas']['ExternalReferencesResourceConfig'];
    };
    /** ExternalReferencesSearchQuery */
    ExternalReferencesSearchQuery: {
      /**
       * @description Type of the resource to search in (enum property replaced by openapi-typescript)
       * @enum {string}
       */
      type: 'externalReferences';
      /**
       * Text
       * @description Text to search for
       * @default
       */
      text?: string;
    };
    /** FocusViewConfig */
    FocusViewConfig: {
      /**
       * Singleline
       * @description Show contents as single line of text when in focus view
       * @default true
       */
      singleLine: boolean;
      /**
       * Delimiter
       * @description Delimiter used for single-line display in focus view
       * @default  /
       */
      delimiter: string;
    };
    /** GeneralApiCallResourceConfig */
    GeneralApiCallResourceConfig: {
      /**
       * Defaultcollapsed
       * @description Whether contents of this resource should be collapsed by default
       * @default false
       */
      defaultCollapsed: boolean;
      /**
       * Font
       * @description Name of a font
       */
      font?: null | string;
    };
    /** GeneralAudioResourceConfig */
    GeneralAudioResourceConfig: {
      /**
       * Defaultcollapsed
       * @description Whether contents of this resource should be collapsed by default
       * @default false
       */
      defaultCollapsed: boolean;
      /**
       * Font
       * @description Name of a font
       */
      font?: null | string;
    };
    /** GeneralExternalReferencesResourceConfig */
    GeneralExternalReferencesResourceConfig: {
      /**
       * Defaultcollapsed
       * @description Whether contents of this resource should be collapsed by default
       * @default false
       */
      defaultCollapsed: boolean;
      /**
       * Font
       * @description Name of a font
       */
      font?: null | string;
    };
    /** GeneralImagesResourceConfig */
    GeneralImagesResourceConfig: {
      /**
       * Defaultcollapsed
       * @description Whether contents of this resource should be collapsed by default
       * @default true
       */
      defaultCollapsed: boolean;
      /**
       * Font
       * @description Name of a font
       */
      font?: null | string;
    };
    /** GeneralPlainTextResourceConfig */
    GeneralPlainTextResourceConfig: {
      /**
       * Defaultcollapsed
       * @description Whether contents of this resource should be collapsed by default
       * @default false
       */
      defaultCollapsed: boolean;
      /**
       * Font
       * @description Name of a font
       */
      font?: null | string;
      /** @default {
       *       "singleLine": true,
       *       "delimiter": " / "
       *     } */
      focusView: components['schemas']['FocusViewConfig'];
      /** @default [] */
      searchReplacements: components['schemas']['SearchReplacements'];
      /** @default [] */
      contentCss: components['schemas']['ContentCssProperties'];
    };
    /** GeneralRichTextResourceConfig */
    GeneralRichTextResourceConfig: {
      /**
       * Defaultcollapsed
       * @description Whether contents of this resource should be collapsed by default
       * @default true
       */
      defaultCollapsed: boolean;
      /**
       * Font
       * @description Name of a font
       */
      font?: null | string;
      /** @default [] */
      searchReplacements: components['schemas']['SearchReplacements'];
      /** @default [] */
      contentCss: components['schemas']['ContentCssProperties'];
    };
    /** GeneralSearchSettings */
    GeneralSearchSettings: {
      /**
       * @description Pagination settings
       * @default {
       *       "pg": 1,
       *       "pgs": 10
       *     }
       */
      pgn?: components['schemas']['PaginationSettings'];
      /** @description Sorting preset */
      sort?: components['schemas']['SortingPreset'];
      /**
       * Strict
       * @default false
       */
      strict: boolean;
    };
    /** GeneralTextAnnotationResourceConfig */
    GeneralTextAnnotationResourceConfig: {
      /**
       * Defaultcollapsed
       * @description Whether contents of this resource should be collapsed by default
       * @default false
       */
      defaultCollapsed: boolean;
      /**
       * Font
       * @description Name of a font
       */
      font?: null | string;
    };
    /** HTTPValidationError */
    HTTPValidationError: {
      /** Detail */
      detail?: components['schemas']['ValidationError'][];
    };
    /** ImageFile */
    ImageFile: {
      /**
       * Url
       * @description URL of the image file
       */
      url: string;
      /**
       * Thumburl
       * @description URL of the image file thumbnail
       */
      thumbUrl?: null | string;
      /**
       * Sourceurl
       * @description URL of the source website of the image
       */
      sourceUrl?: null | string;
      /**
       * Caption
       * @description Caption of the image
       */
      caption?: null | string;
    };
    /** ImagesContentCreate */
    ImagesContentCreate: {
      /**
       * Resourceid
       * @description Resource ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      resourceId: string;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'images';
      /**
       * Locationid
       * @description Text location ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      locationId: string;
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: null | string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: null | string;
      /**
       * Files
       * @description List of image file objects
       */
      files: components['schemas']['ImageFile'][];
    };
    /** ImagesContentRead */
    ImagesContentRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Resourceid
       * @description Resource ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      resourceId: string;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'images';
      /**
       * Locationid
       * @description Text location ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      locationId: string;
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: null | string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: null | string;
      /**
       * Files
       * @description List of image file objects
       */
      files: components['schemas']['ImageFile'][];
    } & {
      [key: string]: unknown;
    };
    /** ImagesContentUpdate */
    ImagesContentUpdate: {
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'images';
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: string;
      /**
       * Files
       * @description List of image file objects
       */
      files?: components['schemas']['ImageFile'][];
    };
    /** ImagesResourceConfig */
    ImagesResourceConfig: {
      /** @default {
       *       "sortOrder": 10,
       *       "defaultActive": true,
       *       "enableContentContext": false,
       *       "searchableQuick": true,
       *       "searchableAdv": true,
       *       "rtl": false
       *     } */
      common: components['schemas']['CommonResourceConfig'];
      /** @default {
       *       "defaultCollapsed": true
       *     } */
      general: components['schemas']['GeneralImagesResourceConfig'];
    };
    /** ImagesResourceCreate */
    ImagesResourceCreate: {
      /**
       * Title
       * @description Title of this resource
       */
      title: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       * @default []
       */
      description: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * Textid
       * @description ID of the text this resource belongs to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      textId: string;
      /**
       * Level
       * @description Text level this resource belongs to
       */
      level: number;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'images';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: null | string;
      /**
       * Meta
       * @description Arbitrary metadata
       * @default []
       */
      meta: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       * @default []
       */
      comment: components['schemas']['ResourceCommentTranslation'][];
      /** @default {
       *       "common": {
       *         "defaultActive": true,
       *         "enableContentContext": false,
       *         "rtl": false,
       *         "searchableAdv": true,
       *         "searchableQuick": true,
       *         "sortOrder": 10
       *       },
       *       "general": {
       *         "defaultCollapsed": true
       *       }
       *     } */
      config: components['schemas']['ImagesResourceConfig'];
    };
    /** ImagesResourceRead */
    ImagesResourceRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Writable
       * @description Whether this resource is writable for the requesting user
       */
      writable?: boolean | null;
      /** @description Public user data for user owning this resource */
      owner?: components['schemas']['UserReadPublic'] | null;
      /**
       * Sharedreadusers
       * @description Public user data for users allowed to read this resource
       */
      sharedReadUsers?: components['schemas']['UserReadPublic'][] | null;
      /**
       * Sharedwriteusers
       * @description Public user data for users allowed to write this resource
       */
      sharedWriteUsers?: components['schemas']['UserReadPublic'][] | null;
      /**
       * Title
       * @description Title of this resource
       */
      title: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       * @default []
       */
      description: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * Textid
       * @description ID of the text this resource belongs to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      textId: string;
      /**
       * Level
       * @description Text level this resource belongs to
       */
      level: number;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'images';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Ownerid
       * @description User owning this resource
       */
      ownerId?: string | null;
      /**
       * Sharedread
       * @description Users with shared read access to this resource
       * @default []
       */
      sharedRead: string[];
      /**
       * Sharedwrite
       * @description Users with shared write access to this resource
       * @default []
       */
      sharedWrite: string[];
      /**
       * Public
       * @description Publication status of this resource
       * @default false
       */
      public: boolean;
      /**
       * Proposed
       * @description Whether this resource has been proposed for publication
       * @default false
       */
      proposed: boolean;
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: null | string;
      /**
       * Meta
       * @description Arbitrary metadata
       * @default []
       */
      meta: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       * @default []
       */
      comment: components['schemas']['ResourceCommentTranslation'][];
      /** @default {
       *       "common": {
       *         "defaultActive": true,
       *         "enableContentContext": false,
       *         "rtl": false,
       *         "searchableAdv": true,
       *         "searchableQuick": true,
       *         "sortOrder": 10
       *       },
       *       "general": {
       *         "defaultCollapsed": true
       *       }
       *     } */
      config: components['schemas']['ImagesResourceConfig'];
      /**
       * Contentschangedat
       * Format: date-time
       * @description The last time contents of this resource changed
       * @default 1970-01-02T00:00:00
       */
      contentsChangedAt: string;
    } & {
      [key: string]: unknown;
    };
    /** ImagesResourceUpdate */
    ImagesResourceUpdate: {
      /**
       * Title
       * @description Title of this resource
       */
      title?: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       */
      description?: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'images';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Sharedread
       * @description Users with shared read access to this resource
       */
      sharedRead?: string[];
      /**
       * Sharedwrite
       * @description Users with shared write access to this resource
       */
      sharedWrite?: string[];
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: string;
      /**
       * Meta
       * @description Arbitrary metadata
       */
      meta?: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       */
      comment?: components['schemas']['ResourceCommentTranslation'][];
      config?: components['schemas']['ImagesResourceConfig'];
    };
    /** ImagesSearchQuery */
    ImagesSearchQuery: {
      /**
       * @description Type of the resource to search in (enum property replaced by openapi-typescript)
       * @enum {string}
       */
      type: 'images';
      /**
       * Caption
       * @description Caption content search query
       * @default
       */
      caption?: string;
    };
    /** IndexInfo */
    IndexInfo: {
      /** Textid */
      textId: string | null;
      /** Documents */
      documents: number;
      /** Size */
      size: string;
      /** Searches */
      searches: number;
      /** Fields */
      fields: number;
      /** Uptodate */
      upToDate: boolean;
    };
    /** LineLabellingConfig */
    LineLabellingConfig: {
      /**
       * Enabled
       * @description Enable/disable line labelling
       * @default false
       */
      enabled: boolean;
      /**
       * Labellingtype
       * @description Line labelling type
       * @default numbersOneBased
       * @enum {string}
       */
      labellingType:
        | 'numbersZeroBased'
        | 'numbersOneBased'
        | 'lettersLowercase'
        | 'lettersUppercase';
    };
    /** @enum {string} */
    LocaleKey: 'deDE' | 'enUS';
    /** LocationCoverage */
    LocationCoverage: {
      /** Locid */
      locId: string;
      /** Label */
      label: string;
      /**
       * Covered
       * @default false
       */
      covered: boolean;
    };
    /** LocationCreate */
    LocationCreate: {
      /**
       * Textid
       * @description ID of the text this location belongs to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      textId: string;
      /**
       * Parentid
       * @description ID of parent location
       */
      parentId?: string | null;
      /**
       * Level
       * @description Index of structure level this location is on
       */
      level: number;
      /**
       * Position
       * @description Position among all text locations on this level
       */
      position: number;
      /**
       * Label
       * @description Label for identifying this text location in level context
       */
      label: string;
      /**
       * Aliases
       * @description List of aliases for this location
       */
      aliases?: string[] | null;
    };
    /** LocationData */
    LocationData: {
      /**
       * Locationpath
       * @description Path of locations from level 0 to this location
       * @default []
       */
      locationPath: components['schemas']['LocationRead'][];
      /**
       * Prev
       * @description ID of the preceding location on the same level
       */
      prev?: string | null;
      /**
       * Next
       * @description ID of the subsequent location on the same level
       */
      next?: string | null;
      /**
       * Contents
       * @description Contents of various resources on this location
       * @default []
       */
      contents: (
        | components['schemas']['ApiCallContentRead']
        | components['schemas']['AudioContentRead']
        | components['schemas']['ExternalReferencesContentRead']
        | components['schemas']['ImagesContentRead']
        | components['schemas']['PlainTextContentRead']
        | components['schemas']['RichTextContentRead']
        | components['schemas']['TextAnnotationContentRead']
      )[];
    };
    /** LocationRead */
    LocationRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Textid
       * @description ID of the text this location belongs to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      textId: string;
      /**
       * Parentid
       * @description ID of parent location
       */
      parentId?: string | null;
      /**
       * Level
       * @description Index of structure level this location is on
       */
      level: number;
      /**
       * Position
       * @description Position among all text locations on this level
       */
      position: number;
      /**
       * Label
       * @description Label for identifying this text location in level context
       */
      label: string;
      /**
       * Aliases
       * @description List of aliases for this location
       */
      aliases?: string[] | null;
    } & {
      [key: string]: unknown;
    };
    /** LocationUpdate */
    LocationUpdate: {
      /**
       * Parentid
       * @description ID of parent location
       */
      parentId?: string | null;
      /**
       * Level
       * @description Index of structure level this location is on
       */
      level?: number;
      /**
       * Position
       * @description Position among all text locations on this level
       */
      position?: number;
      /**
       * Label
       * @description Label for identifying this text location in level context
       */
      label?: string;
      /**
       * Aliases
       * @description List of aliases for this location
       */
      aliases?: string[] | null;
    };
    /** MainNavEntryTranslation */
    MainNavEntryTranslation: {
      locale: components['schemas']['TranslationLocaleKey'];
      /** Translation */
      translation: string;
    };
    /** MetadataEntry */
    MetadataEntry: {
      /**
       * Key
       * @description Key identifying this metadata entry
       */
      key: string;
      /**
       * Value
       * @description Value of this metadata entry
       */
      value: string;
    };
    /** MoveLocationRequestBody */
    MoveLocationRequestBody: {
      /** Position */
      position: number;
      /** After */
      after: boolean;
      /** Parentid */
      parentId: string | null;
    };
    /** OskMode */
    OskMode: {
      /**
       * Key
       * @description Key identifying an OSK mode
       */
      key: string;
      /** Name */
      name: string;
      /**
       * Font
       * @description Name of a font
       */
      font?: null | string;
    };
    /** PaginationSettings */
    PaginationSettings: {
      /**
       * Pg
       * @description Page number
       * @default 1
       */
      pg?: number;
      /**
       * Pgs
       * @description Page size
       * @default 10
       */
      pgs?: number;
    };
    /** ParentCoverage */
    ParentCoverage: {
      /** Label */
      label: string | null;
      /** Locations */
      locations: components['schemas']['LocationCoverage'][];
    };
    /** PlainTextContentCreate */
    PlainTextContentCreate: {
      /**
       * Resourceid
       * @description Resource ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      resourceId: string;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'plainText';
      /**
       * Locationid
       * @description Text location ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      locationId: string;
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: null | string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: null | string;
      /**
       * Text
       * @description Text content of the plain text content object
       */
      text: string;
    };
    /** PlainTextContentRead */
    PlainTextContentRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Resourceid
       * @description Resource ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      resourceId: string;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'plainText';
      /**
       * Locationid
       * @description Text location ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      locationId: string;
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: null | string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: null | string;
      /**
       * Text
       * @description Text content of the plain text content object
       */
      text: string;
    } & {
      [key: string]: unknown;
    };
    /** PlainTextContentUpdate */
    PlainTextContentUpdate: {
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'plainText';
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: string;
      /**
       * Text
       * @description Text content of the plain text content object
       */
      text?: string;
    };
    /** PlainTextResourceConfig */
    PlainTextResourceConfig: {
      /** @default {
       *       "sortOrder": 10,
       *       "defaultActive": true,
       *       "enableContentContext": false,
       *       "searchableQuick": true,
       *       "searchableAdv": true,
       *       "rtl": false
       *     } */
      common: components['schemas']['CommonResourceConfig'];
      /** @default {
       *       "defaultCollapsed": false,
       *       "focusView": {
       *         "delimiter": " / ",
       *         "singleLine": true
       *       },
       *       "searchReplacements": [],
       *       "contentCss": []
       *     } */
      general: components['schemas']['GeneralPlainTextResourceConfig'];
      /** @default {
       *       "lineLabelling": {
       *         "enabled": false,
       *         "labellingType": "numbersOneBased"
       *       },
       *       "deeplLinks": {
       *         "enabled": false
       *       }
       *     } */
      plainText: components['schemas']['PlainTextSpecialConfig'];
    };
    /** PlainTextResourceCreate */
    PlainTextResourceCreate: {
      /**
       * Title
       * @description Title of this resource
       */
      title: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       * @default []
       */
      description: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * Textid
       * @description ID of the text this resource belongs to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      textId: string;
      /**
       * Level
       * @description Text level this resource belongs to
       */
      level: number;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'plainText';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: null | string;
      /**
       * Meta
       * @description Arbitrary metadata
       * @default []
       */
      meta: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       * @default []
       */
      comment: components['schemas']['ResourceCommentTranslation'][];
      /** @default {
       *       "common": {
       *         "defaultActive": true,
       *         "enableContentContext": false,
       *         "rtl": false,
       *         "searchableAdv": true,
       *         "searchableQuick": true,
       *         "sortOrder": 10
       *       },
       *       "general": {
       *         "contentCss": [],
       *         "defaultCollapsed": false,
       *         "focusView": {
       *           "delimiter": " / ",
       *           "singleLine": true
       *         },
       *         "searchReplacements": []
       *       },
       *       "plainText": {
       *         "deeplLinks": {
       *           "enabled": false
       *         },
       *         "lineLabelling": {
       *           "enabled": false,
       *           "labellingType": "numbersOneBased"
       *         }
       *       }
       *     } */
      config: components['schemas']['PlainTextResourceConfig'];
    };
    /** PlainTextResourceRead */
    PlainTextResourceRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Writable
       * @description Whether this resource is writable for the requesting user
       */
      writable?: boolean | null;
      /** @description Public user data for user owning this resource */
      owner?: components['schemas']['UserReadPublic'] | null;
      /**
       * Sharedreadusers
       * @description Public user data for users allowed to read this resource
       */
      sharedReadUsers?: components['schemas']['UserReadPublic'][] | null;
      /**
       * Sharedwriteusers
       * @description Public user data for users allowed to write this resource
       */
      sharedWriteUsers?: components['schemas']['UserReadPublic'][] | null;
      /**
       * Title
       * @description Title of this resource
       */
      title: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       * @default []
       */
      description: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * Textid
       * @description ID of the text this resource belongs to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      textId: string;
      /**
       * Level
       * @description Text level this resource belongs to
       */
      level: number;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'plainText';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Ownerid
       * @description User owning this resource
       */
      ownerId?: string | null;
      /**
       * Sharedread
       * @description Users with shared read access to this resource
       * @default []
       */
      sharedRead: string[];
      /**
       * Sharedwrite
       * @description Users with shared write access to this resource
       * @default []
       */
      sharedWrite: string[];
      /**
       * Public
       * @description Publication status of this resource
       * @default false
       */
      public: boolean;
      /**
       * Proposed
       * @description Whether this resource has been proposed for publication
       * @default false
       */
      proposed: boolean;
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: null | string;
      /**
       * Meta
       * @description Arbitrary metadata
       * @default []
       */
      meta: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       * @default []
       */
      comment: components['schemas']['ResourceCommentTranslation'][];
      /** @default {
       *       "common": {
       *         "defaultActive": true,
       *         "enableContentContext": false,
       *         "rtl": false,
       *         "searchableAdv": true,
       *         "searchableQuick": true,
       *         "sortOrder": 10
       *       },
       *       "general": {
       *         "contentCss": [],
       *         "defaultCollapsed": false,
       *         "focusView": {
       *           "delimiter": " / ",
       *           "singleLine": true
       *         },
       *         "searchReplacements": []
       *       },
       *       "plainText": {
       *         "deeplLinks": {
       *           "enabled": false
       *         },
       *         "lineLabelling": {
       *           "enabled": false,
       *           "labellingType": "numbersOneBased"
       *         }
       *       }
       *     } */
      config: components['schemas']['PlainTextResourceConfig'];
      /**
       * Contentschangedat
       * Format: date-time
       * @description The last time contents of this resource changed
       * @default 1970-01-02T00:00:00
       */
      contentsChangedAt: string;
    } & {
      [key: string]: unknown;
    };
    /** PlainTextResourceUpdate */
    PlainTextResourceUpdate: {
      /**
       * Title
       * @description Title of this resource
       */
      title?: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       */
      description?: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'plainText';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Sharedread
       * @description Users with shared read access to this resource
       */
      sharedRead?: string[];
      /**
       * Sharedwrite
       * @description Users with shared write access to this resource
       */
      sharedWrite?: string[];
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: string;
      /**
       * Meta
       * @description Arbitrary metadata
       */
      meta?: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       */
      comment?: components['schemas']['ResourceCommentTranslation'][];
      config?: components['schemas']['PlainTextResourceConfig'];
    };
    /** PlainTextSearchQuery */
    PlainTextSearchQuery: {
      /**
       * @description Type of the resource to search in (enum property replaced by openapi-typescript)
       * @enum {string}
       */
      type: 'plainText';
      /**
       * Text
       * @description Text content search query
       * @default
       */
      text?: string;
    };
    /**
     * PlainTextSpecialConfig
     * @description Config properties specific to the plain text resource type
     */
    PlainTextSpecialConfig: {
      /** @default {
       *       "enabled": false,
       *       "labellingType": "numbersOneBased"
       *     } */
      lineLabelling: components['schemas']['LineLabellingConfig'];
      /** @default {
       *       "enabled": false
       *     } */
      deeplLinks: components['schemas']['DeepLLinksConfig'];
    };
    /**
     * PlatformData
     * @description Platform data used by the web client
     */
    PlatformData: {
      /** Texts */
      texts: components['schemas']['TextRead'][];
      state: components['schemas']['PlatformStateRead'];
      security: components['schemas']['PlatformSecurityInfo'];
      /** Systemsegments */
      systemSegments: components['schemas']['ClientSegmentRead'][];
      /** Infosegments */
      infoSegments: components['schemas']['ClientSegmentHead'][];
      /** Tekst */
      tekst: {
        [key: string]: string;
      };
    };
    /** PlatformDescriptionTranslation */
    PlatformDescriptionTranslation: {
      locale: components['schemas']['TranslationLocaleKey'];
      /** Translation */
      translation: string;
    };
    /** PlatformSecurityInfo */
    PlatformSecurityInfo: {
      /**
       * Closedmode
       * @default false
       */
      closedMode: boolean;
      /**
       * Usersactivebydefault
       * @default false
       */
      usersActiveByDefault: boolean;
      /**
       * Enablecookieauth
       * @default true
       */
      enableCookieAuth: boolean;
      /**
       * Enablejwtauth
       * @default false
       */
      enableJwtAuth: boolean;
      /**
       * Authcookielifetime
       * @default 10800
       */
      authCookieLifetime: number;
    };
    /** PlatformStateRead */
    PlatformStateRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Platformname
       * @description Name of the platform
       * @default Tekst-Dev
       */
      platformName: string;
      /**
       * Platformsubtitle
       * @description Short description of the platform, in multiple languages
       * @default [
       *       {
       *         "locale": "*",
       *         "translation": "An online text research platform"
       *       }
       *     ]
       */
      platformSubtitle: components['schemas']['PlatformDescriptionTranslation'][];
      /**
       * Availablelocales
       * @description Locales available for use in platform client
       * @default [
       *       "deDE",
       *       "enUS"
       *     ]
       */
      availableLocales: components['schemas']['LocaleKey'][];
      /**
       * Defaulttextid
       * @description Default text to load in UI
       */
      defaultTextId?: string | null;
      /**
       * Indexunpublishedresources
       * @description Index unpublished resources
       * @default false
       */
      indexUnpublishedResources: boolean;
      /**
       * Directjumponuniquealiassearch
       * @description Directly jump to respective location when searching for unique location alias
       * @default true
       */
      directJumpOnUniqueAliasSearch: boolean;
      /**
       * Navbrowseentry
       * @description Custom label for main navigation browse entry
       * @default []
       */
      navBrowseEntry: components['schemas']['MainNavEntryTranslation'][];
      /**
       * Navsearchentry
       * @description Custom label for main navigation search entry
       * @default []
       */
      navSearchEntry: components['schemas']['MainNavEntryTranslation'][];
      /**
       * Navinfoentry
       * @description Custom label for main navigation info entry
       * @default []
       */
      navInfoEntry: components['schemas']['MainNavEntryTranslation'][];
      /**
       * Showresourcecategoryheadings
       * @description Show resource category headings in browse view
       * @default true
       */
      showResourceCategoryHeadings: boolean;
      /**
       * Prioritizebrowselevelresources
       * @description Display resources of current browse level before others in browse view
       * @default true
       */
      prioritizeBrowseLevelResources: boolean;
      /**
       * Showlocationaliases
       * @description Show location aliases in browse view
       * @default true
       */
      showLocationAliases: boolean;
      /**
       * Showlogoonloadingscreen
       * @description Show logo on loading screen
       * @default true
       */
      showLogoOnLoadingScreen: boolean;
      /**
       * Showlogoinheader
       * @description Show logo in page header
       * @default true
       */
      showLogoInHeader: boolean;
      /**
       * Showtekstfooterhint
       * @description Show a small hint to the Tekst software in the footer
       * @default true
       */
      showTekstFooterHint: boolean;
      /**
       * Denyresourcetypes
       * @description Resource types regular users are not allowed to create
       * @default [
       *       "apiCall"
       *     ]
       */
      denyResourceTypes: string[];
      /**
       * Fonts
       * @description CSS font family names for use in resources
       * @default []
       */
      fonts: string[];
      /**
       * Oskmodes
       * @description OSK modes available for use in platform client
       * @default []
       */
      oskModes: components['schemas']['OskMode'][];
      /**
       * Indicesupdatedat
       * @description Time when indices were created
       */
      indicesUpdatedAt?: string | null;
      /**
       * Dbversion
       * @description Version string of DB data
       */
      dbVersion?: null | string;
    } & {
      [key: string]: unknown;
    };
    /** PlatformStateUpdate */
    PlatformStateUpdate: {
      /**
       * Platformname
       * @description Name of the platform
       */
      platformName?: string;
      /**
       * Platformsubtitle
       * @description Short description of the platform, in multiple languages
       */
      platformSubtitle?: components['schemas']['PlatformDescriptionTranslation'][];
      /**
       * Availablelocales
       * @description Locales available for use in platform client
       */
      availableLocales?: components['schemas']['LocaleKey'][];
      /**
       * Defaulttextid
       * @description Default text to load in UI
       */
      defaultTextId?: string | null;
      /**
       * Indexunpublishedresources
       * @description Index unpublished resources
       */
      indexUnpublishedResources?: boolean;
      /**
       * Directjumponuniquealiassearch
       * @description Directly jump to respective location when searching for unique location alias
       */
      directJumpOnUniqueAliasSearch?: boolean;
      /**
       * Navbrowseentry
       * @description Custom label for main navigation browse entry
       */
      navBrowseEntry?: components['schemas']['MainNavEntryTranslation'][];
      /**
       * Navsearchentry
       * @description Custom label for main navigation search entry
       */
      navSearchEntry?: components['schemas']['MainNavEntryTranslation'][];
      /**
       * Navinfoentry
       * @description Custom label for main navigation info entry
       */
      navInfoEntry?: components['schemas']['MainNavEntryTranslation'][];
      /**
       * Showresourcecategoryheadings
       * @description Show resource category headings in browse view
       */
      showResourceCategoryHeadings?: boolean;
      /**
       * Prioritizebrowselevelresources
       * @description Display resources of current browse level before others in browse view
       */
      prioritizeBrowseLevelResources?: boolean;
      /**
       * Showlocationaliases
       * @description Show location aliases in browse view
       */
      showLocationAliases?: boolean;
      /**
       * Showlogoonloadingscreen
       * @description Show logo on loading screen
       */
      showLogoOnLoadingScreen?: boolean;
      /**
       * Showlogoinheader
       * @description Show logo in page header
       */
      showLogoInHeader?: boolean;
      /**
       * Showtekstfooterhint
       * @description Show a small hint to the Tekst software in the footer
       */
      showTekstFooterHint?: boolean;
      /**
       * Denyresourcetypes
       * @description Resource types regular users are not allowed to create
       */
      denyResourceTypes?: string[];
      /**
       * Fonts
       * @description CSS font family names for use in resources
       */
      fonts?: string[];
      /**
       * Oskmodes
       * @description OSK modes available for use in platform client
       */
      oskModes?: components['schemas']['OskMode'][];
    };
    /** @enum {string} */
    PrivateUserProp: 'name' | 'affiliation' | 'bio';
    PrivateUserProps: components['schemas']['PrivateUserProp'][];
    /** PublicUsersSearchResult */
    PublicUsersSearchResult: {
      /**
       * Users
       * @description Paginated public users data
       * @default []
       */
      users: components['schemas']['UserReadPublic'][];
      /**
       * Total
       * @description Total number of search hits
       * @default 0
       */
      total: number;
    };
    /** QuickSearchRequestBody */
    QuickSearchRequestBody: {
      /**
       * @description Search type (enum property replaced by openapi-typescript)
       * @enum {string}
       */
      type: 'quick';
      /**
       * Q
       * @description Query string
       * @default *
       */
      q?: string;
      /**
       * @description General search settings
       * @default {
       *       "pgn": {
       *         "pg": 1,
       *         "pgs": 10
       *       },
       *       "strict": false
       *     }
       */
      gen?: components['schemas']['GeneralSearchSettings'];
      /**
       * @description Quick search settings
       * @default {
       *       "op": "OR",
       *       "re": false,
       *       "inh": false,
       *       "allLvls": false
       *     }
       */
      qck?: components['schemas']['QuickSearchSettings'];
    };
    /** QuickSearchSettings */
    QuickSearchSettings: {
      /**
       * Op
       * @description Default operator
       * @default OR
       * @enum {string}
       */
      op?: 'AND' | 'OR';
      /**
       * Re
       * @description Whether to use regular expressions
       * @default false
       */
      re?: boolean;
      /**
       * Inh
       * @description Whether to match contents inherited from higher-level locations
       * @default false
       */
      inh?: boolean;
      /**
       * Alllvls
       * @description Whether to find locations from all levels, as opposed to only finding locations from the respective text's default level
       * @default false
       */
      allLvls?: boolean;
      /**
       * Txt
       * @description IDs of texts to search in
       */
      txt?: string[] | null;
    };
    /** ResourceCategory */
    ResourceCategory: {
      /**
       * Key
       * @description Key identifying this resource category
       */
      key: string;
      /** Translations */
      translations: components['schemas']['ResourceCategoryTranslation'][];
    };
    /** ResourceCategoryTranslation */
    ResourceCategoryTranslation: {
      locale: components['schemas']['TranslationLocaleKey'];
      /**
       * Translation
       * @description Translation of a resource category
       */
      translation: string;
    };
    /** ResourceCommentTranslation */
    ResourceCommentTranslation: {
      locale: components['schemas']['TranslationLocaleKey'];
      /**
       * Translation
       * @description Comment translation HTML for this resource
       */
      translation: string;
    };
    /** ResourceCoverage */
    ResourceCoverage: {
      /** Covered */
      covered: number;
      /** Total */
      total: number;
      /** Ranges */
      ranges: string[][];
      /** Rangescovered */
      rangesCovered: boolean;
      /** Details */
      details: components['schemas']['ParentCoverage'][];
    };
    /** ResourceDescriptionTranslation */
    ResourceDescriptionTranslation: {
      locale: components['schemas']['TranslationLocaleKey'];
      /**
       * Translation
       * @description Description translation for this resource
       */
      translation: string;
    };
    /** ResourceSearchQuery */
    ResourceSearchQuery: {
      /** @description Common resource search query data */
      cmn: components['schemas']['CommonResourceSearchQueryData'];
      /**
       * Rts
       * @description Resource type-specific search query data
       */
      rts:
        | components['schemas']['AudioSearchQuery']
        | components['schemas']['ExternalReferencesSearchQuery']
        | components['schemas']['ImagesSearchQuery']
        | components['schemas']['PlainTextSearchQuery']
        | components['schemas']['RichTextSearchQuery']
        | components['schemas']['TextAnnotationSearchQuery'];
    };
    /** ResourceTitleTranslation */
    ResourceTitleTranslation: {
      locale: components['schemas']['TranslationLocaleKey'];
      /**
       * Translation
       * @description Title translation for this resource
       */
      translation: string;
    };
    /** RichTextContentCreate */
    RichTextContentCreate: {
      /**
       * Resourceid
       * @description Resource ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      resourceId: string;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'richText';
      /**
       * Locationid
       * @description Text location ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      locationId: string;
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: null | string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: null | string;
      /**
       * Html
       * @description HTML content of the rich text content object
       */
      html: string;
      /**
       * Editormode
       * @description Last used editor mode for this content
       * @default wysiwyg
       * @enum {string}
       */
      editorMode: 'wysiwyg' | 'html';
    };
    /** RichTextContentRead */
    RichTextContentRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Resourceid
       * @description Resource ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      resourceId: string;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'richText';
      /**
       * Locationid
       * @description Text location ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      locationId: string;
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: null | string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: null | string;
      /**
       * Html
       * @description HTML content of the rich text content object
       */
      html: string;
      /**
       * Editormode
       * @description Last used editor mode for this content
       * @default wysiwyg
       * @enum {string}
       */
      editorMode: 'wysiwyg' | 'html';
    } & {
      [key: string]: unknown;
    };
    /** RichTextContentUpdate */
    RichTextContentUpdate: {
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'richText';
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: string;
      /**
       * Html
       * @description HTML content of the rich text content object
       */
      html?: string;
      /**
       * Editormode
       * @description Last used editor mode for this content
       */
      editorMode?: 'wysiwyg' | 'html';
    };
    /** RichTextResourceConfig */
    RichTextResourceConfig: {
      /** @default {
       *       "sortOrder": 10,
       *       "defaultActive": true,
       *       "enableContentContext": false,
       *       "searchableQuick": true,
       *       "searchableAdv": true,
       *       "rtl": false
       *     } */
      common: components['schemas']['CommonResourceConfig'];
      /** @default {
       *       "defaultCollapsed": true,
       *       "searchReplacements": [],
       *       "contentCss": []
       *     } */
      general: components['schemas']['GeneralRichTextResourceConfig'];
    };
    /** RichTextResourceCreate */
    RichTextResourceCreate: {
      /**
       * Title
       * @description Title of this resource
       */
      title: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       * @default []
       */
      description: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * Textid
       * @description ID of the text this resource belongs to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      textId: string;
      /**
       * Level
       * @description Text level this resource belongs to
       */
      level: number;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'richText';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: null | string;
      /**
       * Meta
       * @description Arbitrary metadata
       * @default []
       */
      meta: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       * @default []
       */
      comment: components['schemas']['ResourceCommentTranslation'][];
      /** @default {
       *       "common": {
       *         "defaultActive": true,
       *         "enableContentContext": false,
       *         "rtl": false,
       *         "searchableAdv": true,
       *         "searchableQuick": true,
       *         "sortOrder": 10
       *       },
       *       "general": {
       *         "contentCss": [],
       *         "defaultCollapsed": true,
       *         "searchReplacements": []
       *       }
       *     } */
      config: components['schemas']['RichTextResourceConfig'];
    };
    /** RichTextResourceRead */
    RichTextResourceRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Writable
       * @description Whether this resource is writable for the requesting user
       */
      writable?: boolean | null;
      /** @description Public user data for user owning this resource */
      owner?: components['schemas']['UserReadPublic'] | null;
      /**
       * Sharedreadusers
       * @description Public user data for users allowed to read this resource
       */
      sharedReadUsers?: components['schemas']['UserReadPublic'][] | null;
      /**
       * Sharedwriteusers
       * @description Public user data for users allowed to write this resource
       */
      sharedWriteUsers?: components['schemas']['UserReadPublic'][] | null;
      /**
       * Title
       * @description Title of this resource
       */
      title: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       * @default []
       */
      description: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * Textid
       * @description ID of the text this resource belongs to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      textId: string;
      /**
       * Level
       * @description Text level this resource belongs to
       */
      level: number;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'richText';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Ownerid
       * @description User owning this resource
       */
      ownerId?: string | null;
      /**
       * Sharedread
       * @description Users with shared read access to this resource
       * @default []
       */
      sharedRead: string[];
      /**
       * Sharedwrite
       * @description Users with shared write access to this resource
       * @default []
       */
      sharedWrite: string[];
      /**
       * Public
       * @description Publication status of this resource
       * @default false
       */
      public: boolean;
      /**
       * Proposed
       * @description Whether this resource has been proposed for publication
       * @default false
       */
      proposed: boolean;
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: null | string;
      /**
       * Meta
       * @description Arbitrary metadata
       * @default []
       */
      meta: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       * @default []
       */
      comment: components['schemas']['ResourceCommentTranslation'][];
      /** @default {
       *       "common": {
       *         "defaultActive": true,
       *         "enableContentContext": false,
       *         "rtl": false,
       *         "searchableAdv": true,
       *         "searchableQuick": true,
       *         "sortOrder": 10
       *       },
       *       "general": {
       *         "contentCss": [],
       *         "defaultCollapsed": true,
       *         "searchReplacements": []
       *       }
       *     } */
      config: components['schemas']['RichTextResourceConfig'];
      /**
       * Contentschangedat
       * Format: date-time
       * @description The last time contents of this resource changed
       * @default 1970-01-02T00:00:00
       */
      contentsChangedAt: string;
    } & {
      [key: string]: unknown;
    };
    /** RichTextResourceUpdate */
    RichTextResourceUpdate: {
      /**
       * Title
       * @description Title of this resource
       */
      title?: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       */
      description?: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'richText';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Sharedread
       * @description Users with shared read access to this resource
       */
      sharedRead?: string[];
      /**
       * Sharedwrite
       * @description Users with shared write access to this resource
       */
      sharedWrite?: string[];
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: string;
      /**
       * Meta
       * @description Arbitrary metadata
       */
      meta?: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       */
      comment?: components['schemas']['ResourceCommentTranslation'][];
      config?: components['schemas']['RichTextResourceConfig'];
    };
    /** RichTextSearchQuery */
    RichTextSearchQuery: {
      /**
       * @description Type of the resource to search in (enum property replaced by openapi-typescript)
       * @enum {string}
       */
      type: 'richText';
      /**
       * Html
       * @description HTML text content search query
       * @default
       */
      html?: string;
    };
    /** SearchHit */
    SearchHit: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /** Label */
      label: string;
      /** Fulllabel */
      fullLabel: string;
      /**
       * Textid
       * @example 5eb7cf5a86d9755df3a6c593
       */
      textId: string;
      /** Level */
      level: number;
      /** Position */
      position: number;
      /** Score */
      score: number | null;
      /**
       * Highlight
       * @default {}
       */
      highlight: {
        [key: string]: string[];
      };
    };
    /** SearchReplacement */
    SearchReplacement: {
      /**
       * Pattern
       * @description Regular expression to match (Java RegEx syntax)
       */
      pattern: string;
      /**
       * Replacement
       * @description Replacement string
       */
      replacement: string;
    };
    SearchReplacements: components['schemas']['SearchReplacement'][];
    /** SearchResults */
    SearchResults: {
      /** Hits */
      hits: components['schemas']['SearchHit'][];
      /** Took */
      took: number;
      /** Totalhits */
      totalHits: number;
      /**
       * Totalhitsrelation
       * @enum {string}
       */
      totalHitsRelation: 'eq' | 'gte';
      /** Maxscore */
      maxScore: number | null;
    };
    /** @enum {string} */
    SortingPreset: 'relevance' | 'text_level_position' | 'text_level_relevance';
    /** TaskRead */
    TaskRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /** @description Type of the task */
      type: components['schemas']['TaskType'];
      /**
       * Targetid
       * @description ID of the target of the task or None if there is no target
       */
      targetId?: string | null;
      /**
       * Userid
       * @description ID of user who created this task
       * @example 5eb7cf5a86d9755df3a6c593
       */
      userId: string;
      /**
       * Pickupkey
       * @description Pickup key for accessing the task in case tasks are requested by a non-authenticated user
       */
      pickupKey: string;
      /**
       * Status
       * @description Status of the task
       * @enum {string}
       */
      status: 'waiting' | 'running' | 'done' | 'failed';
      /**
       * Starttime
       * Format: date-time
       * @description Time when the task was started
       */
      startTime: string;
      /**
       * Endtime
       * @description Time when the task has ended
       */
      endTime?: string | null;
      /**
       * Durationseconds
       * @description Duration of the finished task in seconds
       */
      durationSeconds?: number | null;
      /**
       * Result
       * @description Result data of the task
       */
      result?: Record<string, never> | null;
      /**
       * Error
       * @description Error message if the task failed
       */
      error?: null | string;
    } & {
      [key: string]: unknown;
    };
    /**
     * TaskType
     * @description Task types with locking and artifact flags
     * @enum {string}
     */
    TaskType:
      | 'indices_create_update'
      | 'resource_import'
      | 'resource_export'
      | 'search_export'
      | 'broadcast_user_ntfc'
      | 'broadcast_admin_ntfc'
      | 'resource_precompute_hook'
      | 'structure_update'
      | 'platform_cleanup';
    /** TekstErrorModel */
    TekstErrorModel: {
      detail: components['schemas']['ErrorDetail'];
    };
    /** TextAnnotationContentCreate */
    TextAnnotationContentCreate: {
      /**
       * Resourceid
       * @description Resource ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      resourceId: string;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'textAnnotation';
      /**
       * Locationid
       * @description Text location ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      locationId: string;
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: null | string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: null | string;
      /**
       * Tokens
       * @description List of annotated tokens in this content object
       */
      tokens: components['schemas']['TextAnnotationToken'][];
    };
    /** TextAnnotationContentRead */
    TextAnnotationContentRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Resourceid
       * @description Resource ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      resourceId: string;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'textAnnotation';
      /**
       * Locationid
       * @description Text location ID
       * @example 5eb7cf5a86d9755df3a6c593
       */
      locationId: string;
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: null | string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: null | string;
      /**
       * Tokens
       * @description List of annotated tokens in this content object
       */
      tokens: components['schemas']['TextAnnotationToken'][];
    } & {
      [key: string]: unknown;
    };
    /** TextAnnotationContentUpdate */
    TextAnnotationContentUpdate: {
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'textAnnotation';
      /**
       * Comment
       * @description Plain text, potentially multiline comment that will be displayed with the content
       */
      comment?: string;
      /**
       * Notes
       * @description Plain text, potentially multiline working notes on this content meant as an aid for people editing this content
       */
      notes?: string;
      /**
       * Tokens
       * @description List of annotated tokens in this content object
       */
      tokens?: components['schemas']['TextAnnotationToken'][];
    };
    /** TextAnnotationEntry */
    TextAnnotationEntry: {
      /**
       * Key
       * @description Key of the annotation
       */
      key: string;
      /** @description Value(s) of the annotation */
      value: components['schemas']['TextAnnotationValues'];
    };
    /** TextAnnotationQueryEntry */
    TextAnnotationQueryEntry: {
      /**
       * K
       * @description Key of the annotation
       */
      k: string;
      /**
       * V
       * @description Value of the annotation
       */
      v?: null | string;
      /**
       * Wc
       * @description Whether to interpret wildcards in the annotation value query
       * @default false
       */
      wc: boolean;
    };
    /** TextAnnotationResourceConfig */
    TextAnnotationResourceConfig: {
      /** @default {
       *       "sortOrder": 10,
       *       "defaultActive": true,
       *       "enableContentContext": false,
       *       "searchableQuick": true,
       *       "searchableAdv": true,
       *       "rtl": false
       *     } */
      common: components['schemas']['CommonResourceConfig'];
      /** @default {
       *       "defaultCollapsed": false
       *     } */
      general: components['schemas']['GeneralTextAnnotationResourceConfig'];
      /** @default {
       *       "annotationGroups": [],
       *       "multiValueDelimiter": "/"
       *     } */
      textAnnotation: components['schemas']['TextAnnotationSpecialConfig'];
    };
    /** TextAnnotationResourceCreate */
    TextAnnotationResourceCreate: {
      /**
       * Title
       * @description Title of this resource
       */
      title: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       * @default []
       */
      description: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * Textid
       * @description ID of the text this resource belongs to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      textId: string;
      /**
       * Level
       * @description Text level this resource belongs to
       */
      level: number;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'textAnnotation';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: null | string;
      /**
       * Meta
       * @description Arbitrary metadata
       * @default []
       */
      meta: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       * @default []
       */
      comment: components['schemas']['ResourceCommentTranslation'][];
      /** @default {
       *       "common": {
       *         "defaultActive": true,
       *         "enableContentContext": false,
       *         "rtl": false,
       *         "searchableAdv": true,
       *         "searchableQuick": true,
       *         "sortOrder": 10
       *       },
       *       "general": {
       *         "defaultCollapsed": false
       *       },
       *       "textAnnotation": {
       *         "annotationGroups": [],
       *         "multiValueDelimiter": "/"
       *       }
       *     } */
      config: components['schemas']['TextAnnotationResourceConfig'];
    };
    /** TextAnnotationResourceRead */
    TextAnnotationResourceRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Writable
       * @description Whether this resource is writable for the requesting user
       */
      writable?: boolean | null;
      /** @description Public user data for user owning this resource */
      owner?: components['schemas']['UserReadPublic'] | null;
      /**
       * Sharedreadusers
       * @description Public user data for users allowed to read this resource
       */
      sharedReadUsers?: components['schemas']['UserReadPublic'][] | null;
      /**
       * Sharedwriteusers
       * @description Public user data for users allowed to write this resource
       */
      sharedWriteUsers?: components['schemas']['UserReadPublic'][] | null;
      /**
       * Title
       * @description Title of this resource
       */
      title: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       * @default []
       */
      description: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * Textid
       * @description ID of the text this resource belongs to
       * @example 5eb7cf5a86d9755df3a6c593
       */
      textId: string;
      /**
       * Level
       * @description Text level this resource belongs to
       */
      level: number;
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'textAnnotation';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Ownerid
       * @description User owning this resource
       */
      ownerId?: string | null;
      /**
       * Sharedread
       * @description Users with shared read access to this resource
       * @default []
       */
      sharedRead: string[];
      /**
       * Sharedwrite
       * @description Users with shared write access to this resource
       * @default []
       */
      sharedWrite: string[];
      /**
       * Public
       * @description Publication status of this resource
       * @default false
       */
      public: boolean;
      /**
       * Proposed
       * @description Whether this resource has been proposed for publication
       * @default false
       */
      proposed: boolean;
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: null | string;
      /**
       * Meta
       * @description Arbitrary metadata
       * @default []
       */
      meta: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       * @default []
       */
      comment: components['schemas']['ResourceCommentTranslation'][];
      /** @default {
       *       "common": {
       *         "defaultActive": true,
       *         "enableContentContext": false,
       *         "rtl": false,
       *         "searchableAdv": true,
       *         "searchableQuick": true,
       *         "sortOrder": 10
       *       },
       *       "general": {
       *         "defaultCollapsed": false
       *       },
       *       "textAnnotation": {
       *         "annotationGroups": [],
       *         "multiValueDelimiter": "/"
       *       }
       *     } */
      config: components['schemas']['TextAnnotationResourceConfig'];
      /**
       * Contentschangedat
       * Format: date-time
       * @description The last time contents of this resource changed
       * @default 1970-01-02T00:00:00
       */
      contentsChangedAt: string;
    } & {
      [key: string]: unknown;
    };
    /** TextAnnotationResourceUpdate */
    TextAnnotationResourceUpdate: {
      /**
       * Title
       * @description Title of this resource
       */
      title?: components['schemas']['ResourceTitleTranslation'][];
      /**
       * Description
       * @description Short, concise description of this resource
       */
      description?: components['schemas']['ResourceDescriptionTranslation'][];
      /**
       * @description discriminator enum property added by openapi-typescript
       * @enum {string}
       */
      resourceType: 'textAnnotation';
      /**
       * Originalid
       * @description If this is a version of another resource, this ID references the original
       */
      originalId?: string | null;
      /**
       * Sharedread
       * @description Users with shared read access to this resource
       */
      sharedRead?: string[];
      /**
       * Sharedwrite
       * @description Users with shared write access to this resource
       */
      sharedWrite?: string[];
      /**
       * Citation
       * @description Citation details for this resource
       */
      citation?: string;
      /**
       * Meta
       * @description Arbitrary metadata
       */
      meta?: components['schemas']['MetadataEntry'][];
      /**
       * Comment
       * @description Plain text, potentially multiline comment on this resource
       */
      comment?: components['schemas']['ResourceCommentTranslation'][];
      config?: components['schemas']['TextAnnotationResourceConfig'];
    };
    /** TextAnnotationSearchQuery */
    TextAnnotationSearchQuery: {
      /**
       * @description Type of the resource to search in (enum property replaced by openapi-typescript)
       * @enum {string}
       */
      type: 'textAnnotation';
      /**
       * Token
       * @description Token search query
       * @default
       */
      token?: string;
      /**
       * Twc
       * @description Whether to interpret wildcards in the token query
       * @default false
       */
      twc?: boolean;
      /**
       * Anno
       * @description List of annotations to match
       * @default []
       */
      anno?: components['schemas']['TextAnnotationQueryEntry'][];
    };
    /**
     * TextAnnotationSpecialConfig
     * @description Config properties specific to the text annotation resource type
     */
    TextAnnotationSpecialConfig: {
      /**
       * Annotationgroups
       * @description Display groups to use for grouping annotations
       * @default []
       */
      annotationGroups: components['schemas']['AnnotationGroup'][];
      /**
       * Displaytemplate
       * @description Template string used for displaying the annotations in the web client(if missing, all annotations are displayed with key and value,separated by commas)
       */
      displayTemplate?: null | string;
      /**
       * Multivaluedelimiter
       * @description String used to delimit multiple values for an annotation
       * @default /
       */
      multiValueDelimiter: string;
    };
    /** TextAnnotationToken */
    TextAnnotationToken: {
      /**
       * Token
       * @description Text token
       */
      token: string;
      /**
       * Annotations
       * @description List of annotations on this token
       * @default []
       */
      annotations: components['schemas']['TextAnnotationEntry'][];
      /**
       * Lb
       * @description Whether this token ends a line
       * @default false
       */
      lb: boolean;
    };
    /** @description Value of an annotation */
    TextAnnotationValue: string;
    /** @description List of values of an annotation */
    TextAnnotationValues: components['schemas']['TextAnnotationValue'][];
    /** TextCreate */
    TextCreate: {
      /**
       * Title
       * @description Title of this text
       */
      title: string;
      /**
       * Slug
       * @description A short identifier for use in URLs and internal operations
       */
      slug: string;
      /**
       * Subtitle
       * @description Subtitle translations of this text (if set, it must contain at least one element)
       * @default []
       */
      subtitle: components['schemas']['TextSubtitleTranslation'][];
      /**
       * Levels
       * @description Structure levels of this text and their label translations
       */
      levels: components['schemas']['TextLevelTranslation'][][];
      /**
       * Defaultlevel
       * @description Default structure level for the client to use for browsing this text
       * @default 0
       */
      defaultLevel: number;
      /**
       * Locdelim
       * @description Delimiter for displaying text locations
       * @default ,
       */
      locDelim: string;
      /**
       * Labeledlocation
       * @description Whether the UI should label the parts of the browse location with each levels' names
       * @default true
       */
      labeledLocation: boolean;
      /**
       * Accentcolor
       * Format: color
       * @description Accent color used for this text in the client UI
       * @default #305D97
       */
      accentColor: string;
      /**
       * Isactive
       * @description Whether the text should be listed for non-admin users in the web client
       * @default false
       */
      isActive: boolean;
      /**
       * Resourcecategories
       * @description Resource categories to categorize resources in
       * @default []
       */
      resourceCategories: components['schemas']['ResourceCategory'][];
      /**
       * Fullloclabelashitheading
       * @description Whether to use the full location label as the hit heading in the search results
       * @default false
       */
      fullLocLabelAsHitHeading: boolean;
    };
    /** TextLevelTranslation */
    TextLevelTranslation: {
      locale: components['schemas']['TranslationLocaleKey'];
      /**
       * Translation
       * @description Translation of a text level label
       */
      translation: string;
    };
    /** TextRead */
    TextRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Title
       * @description Title of this text
       */
      title: string;
      /**
       * Slug
       * @description A short identifier for use in URLs and internal operations
       */
      slug: string;
      /**
       * Subtitle
       * @description Subtitle translations of this text (if set, it must contain at least one element)
       * @default []
       */
      subtitle: components['schemas']['TextSubtitleTranslation'][];
      /**
       * Levels
       * @description Structure levels of this text and their label translations
       */
      levels: components['schemas']['TextLevelTranslation'][][];
      /**
       * Defaultlevel
       * @description Default structure level for the client to use for browsing this text
       * @default 0
       */
      defaultLevel: number;
      /**
       * Locdelim
       * @description Delimiter for displaying text locations
       * @default ,
       */
      locDelim: string;
      /**
       * Labeledlocation
       * @description Whether the UI should label the parts of the browse location with each levels' names
       * @default true
       */
      labeledLocation: boolean;
      /**
       * Accentcolor
       * Format: color
       * @description Accent color used for this text in the client UI
       * @default #305D97
       */
      accentColor: string;
      /**
       * Isactive
       * @description Whether the text should be listed for non-admin users in the web client
       * @default false
       */
      isActive: boolean;
      /**
       * Resourcecategories
       * @description Resource categories to categorize resources in
       * @default []
       */
      resourceCategories: components['schemas']['ResourceCategory'][];
      /**
       * Fullloclabelashitheading
       * @description Whether to use the full location label as the hit heading in the search results
       * @default false
       */
      fullLocLabelAsHitHeading: boolean;
      /**
       * Indexutd
       * @description The search index for this text is up-to-date
       * @default false
       */
      indexUtd: boolean;
    } & {
      [key: string]: unknown;
    };
    /** TextSubtitleTranslation */
    TextSubtitleTranslation: {
      locale: components['schemas']['TranslationLocaleKey'];
      /**
       * Translation
       * @description Subtitle translation for a text
       */
      translation: string;
    };
    /** TextUpdate */
    TextUpdate: {
      /**
       * Title
       * @description Title of this text
       */
      title?: string;
      /**
       * Slug
       * @description A short identifier for use in URLs and internal operations
       */
      slug?: string;
      /**
       * Subtitle
       * @description Subtitle translations of this text (if set, it must contain at least one element)
       */
      subtitle?: components['schemas']['TextSubtitleTranslation'][];
      /**
       * Levels
       * @description Structure levels of this text and their label translations
       */
      levels?: components['schemas']['TextLevelTranslation'][][];
      /**
       * Defaultlevel
       * @description Default structure level for the client to use for browsing this text
       */
      defaultLevel?: number;
      /**
       * Locdelim
       * @description Delimiter for displaying text locations
       */
      locDelim?: string;
      /**
       * Labeledlocation
       * @description Whether the UI should label the parts of the browse location with each levels' names
       */
      labeledLocation?: boolean;
      /**
       * Accentcolor
       * @description Accent color used for this text in the client UI
       */
      accentColor?: string;
      /**
       * Isactive
       * @description Whether the text should be listed for non-admin users in the web client
       */
      isActive?: boolean;
      /**
       * Resourcecategories
       * @description Resource categories to categorize resources in
       */
      resourceCategories?: components['schemas']['ResourceCategory'][];
      /**
       * Fullloclabelashitheading
       * @description Whether to use the full location label as the hit heading in the search results
       */
      fullLocLabelAsHitHeading?: boolean;
    };
    /** @enum {string} */
    TranslationLocaleKey: 'deDE' | 'enUS' | '*';
    /**
     * UserCreate
     * @description Dataset for creating a new user
     */
    UserCreate: {
      /**
       * Email
       * Format: email
       */
      email: string;
      /** Password */
      password: string;
      /**
       * Isactive
       * @default false
       */
      isActive: boolean;
      /**
       * Issuperuser
       * @default false
       */
      isSuperuser: boolean | null;
      /**
       * Isverified
       * @default false
       */
      isVerified: boolean | null;
      /**
       * Username
       * @description Public username of this user
       */
      username: string;
      /**
       * Name
       * @description Full name of this user
       */
      name: string;
      /**
       * Affiliation
       * @description Affiliation info of this user
       */
      affiliation: string;
      /** @description Key of the locale used by this user */
      locale?: components['schemas']['LocaleKey'] | null;
      /**
       * Avatarurl
       * @description URL of this user's avatar picture
       */
      avatarUrl?: null | string;
      /**
       * Bio
       * @description Biography of this user
       */
      bio?: null | string;
      /** @default [] */
      publicFields: components['schemas']['PrivateUserProps'];
      /**
       * Usernotificationtriggers
       * @description Events that trigger notifications for this user
       * @default [
       *       "messageReceived",
       *       "newCorrection",
       *       "resourceProposed",
       *       "resourcePublished"
       *     ]
       */
      userNotificationTriggers: components['schemas']['UserNotificationTrigger'][];
      /**
       * Adminnotificationtriggers
       * @description Events that trigger admin notifications for this user
       * @default [
       *       "userAwaitsActivation",
       *       "newCorrection"
       *     ]
       */
      adminNotificationTriggers: components['schemas']['AdminNotificationTrigger'][];
      /** Seen */
      seen?: boolean | null;
    };
    /** UserMessageCreate */
    UserMessageCreate: {
      /**
       * Sender
       * @description ID of the sender or None if this is a system message
       */
      sender?: string | null;
      /**
       * Recipient
       * @description ID of the recipient
       * @example 5eb7cf5a86d9755df3a6c593
       */
      recipient: string;
      /**
       * Content
       * @description Content of the message
       */
      content: string;
    };
    /** UserMessageRead */
    UserMessageRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Sender
       * @description ID of the sender or None if this is a system message
       */
      sender?: string | null;
      /**
       * Recipient
       * @description ID of the recipient
       * @example 5eb7cf5a86d9755df3a6c593
       */
      recipient: string;
      /**
       * Content
       * @description Content of the message
       */
      content: string;
      /**
       * Createdat
       * Format: date-time
       * @description Time when the message was sent
       */
      createdAt: string;
      /**
       * Read
       * @description Whether the message has been read by the recipient
       * @default false
       */
      read: boolean;
      /**
       * Deleted
       * @description ID of the user who deleted the message or None if not deleted
       */
      deleted?: string | null;
    } & {
      [key: string]: unknown;
    };
    /** UserMessageThread */
    UserMessageThread: {
      /**
       * Id
       * @description ID of the thread or None if the message is a system message
       */
      id: string | null;
      /** @description User data for the other user participating in this thread */
      contact: components['schemas']['UserReadPublic'] | null;
      /**
       * Unread
       * @description Number of unread messages in this thread
       */
      unread: number;
    };
    /** @enum {string} */
    UserNotificationTrigger:
      | 'messageReceived'
      | 'newCorrection'
      | 'resourceProposed'
      | 'resourcePublished';
    /**
     * UserRead
     * @description A user registered in the system
     */
    UserRead: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /**
       * Email
       * Format: email
       */
      email: string;
      /** Isactive */
      isActive: boolean;
      /** Issuperuser */
      isSuperuser: boolean;
      /** Isverified */
      isVerified: boolean;
      /**
       * Username
       * @description Public username of this user
       */
      username: string;
      /**
       * Name
       * @description Full name of this user
       */
      name: string;
      /**
       * Affiliation
       * @description Affiliation info of this user
       */
      affiliation: string;
      /** @description Key of the locale used by this user */
      locale?: components['schemas']['LocaleKey'] | null;
      /**
       * Avatarurl
       * @description URL of this user's avatar picture
       */
      avatarUrl?: null | string;
      /**
       * Bio
       * @description Biography of this user
       */
      bio?: null | string;
      /** @default [] */
      publicFields: components['schemas']['PrivateUserProps'];
      /**
       * Usernotificationtriggers
       * @description Events that trigger notifications for this user
       * @default [
       *       "messageReceived",
       *       "newCorrection",
       *       "resourceProposed",
       *       "resourcePublished"
       *     ]
       */
      userNotificationTriggers: components['schemas']['UserNotificationTrigger'][];
      /**
       * Adminnotificationtriggers
       * @description Events that trigger admin notifications for this user
       * @default [
       *       "userAwaitsActivation",
       *       "newCorrection"
       *     ]
       */
      adminNotificationTriggers: components['schemas']['AdminNotificationTrigger'][];
      /** Seen */
      seen?: boolean | null;
      /**
       * Createdat
       * Format: date-time
       */
      createdAt: string;
    };
    /** UserReadPublic */
    UserReadPublic: {
      /**
       * Id
       * @example 5eb7cf5a86d9755df3a6c593
       */
      id: string;
      /** Username */
      username: string;
      /** Name */
      name?: string | null;
      /** Affiliation */
      affiliation?: string | null;
      /** Avatarurl */
      avatarUrl?: null | string;
      /** Bio */
      bio?: string | null;
      /** Isactive */
      isActive: boolean;
      /** Issuperuser */
      isSuperuser: boolean;
      publicFields: components['schemas']['PrivateUserProps'];
    };
    /** UserUpdate */
    UserUpdate: {
      /** Password */
      password?: string | null;
      /** Email */
      email?: string | null;
      /** Isactive */
      isActive?: boolean | null;
      /** Issuperuser */
      isSuperuser?: boolean | null;
      /** Isverified */
      isVerified?: boolean | null;
      /**
       * Username
       * @description Public username of this user
       */
      username?: string;
      /**
       * Name
       * @description Full name of this user
       */
      name?: string;
      /**
       * Affiliation
       * @description Affiliation info of this user
       */
      affiliation?: string;
      /** @description Key of the locale used by this user */
      locale?: components['schemas']['LocaleKey'] | null;
      /**
       * Avatarurl
       * @description URL of this user's avatar picture
       */
      avatarUrl?: string;
      /**
       * Bio
       * @description Biography of this user
       */
      bio?: string;
      publicFields?: components['schemas']['PrivateUserProps'];
      /**
       * Usernotificationtriggers
       * @description Events that trigger notifications for this user
       */
      userNotificationTriggers?: components['schemas']['UserNotificationTrigger'][];
      /**
       * Adminnotificationtriggers
       * @description Events that trigger admin notifications for this user
       */
      adminNotificationTriggers?: components['schemas']['AdminNotificationTrigger'][];
      /** Seen */
      seen?: boolean | null;
    };
    /** UsersSearchResult */
    UsersSearchResult: {
      /**
       * Users
       * @description Paginated users data
       * @default []
       */
      users: components['schemas']['UserRead'][];
      /**
       * Total
       * @description Total number of search hits
       * @default 0
       */
      total: number;
    };
    /** ValidationError */
    ValidationError: {
      /** Location */
      loc: (string | number)[];
      /** Message */
      msg: string;
      /** Error Type */
      type: string;
    };
  };
  responses: never;
  parameters: never;
  requestBodies: never;
  headers: never;
  pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
  deleteBookmark: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      204: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getUserBookmarks: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['BookmarkRead'][];
        };
      };
    };
  };
  createBookmark: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['BookmarkCreate'];
      };
    };
    responses: {
      /** @description Successful Response */
      201: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['BookmarkRead'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Conflict */
      409: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getContentContext: {
    parameters: {
      query: {
        /** @description ID of resource the requested contents belong to */
        res: string;
        /** @description ID of parent location to get child contents for */
        parent?: string | null;
      };
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': (
            | components['schemas']['ApiCallContentRead']
            | components['schemas']['AudioContentRead']
            | components['schemas']['ExternalReferencesContentRead']
            | components['schemas']['ImagesContentRead']
            | components['schemas']['PlainTextContentRead']
            | components['schemas']['RichTextContentRead']
            | components['schemas']['TextAnnotationContentRead']
          )[];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getLocationData: {
    parameters: {
      query?: {
        /** @description ID of location to request data for */
        id?: string | null;
        /** @description ID of text the target location belongs to (needed if no location ID is given) */
        txt?: string | null;
        /** @description Location level (only used if no location ID is given, text's default level is used by default) */
        lvl?: number | null;
        /** @description Location position (only used if no location ID is given) */
        pos?: number;
        /** @description List of IDs of resources to return contents for (assumes all if none are given) */
        res?: string[];
        /** @description Only return contents for the head location of the path */
        head?: boolean;
      };
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['LocationData'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getNearestContentLocation: {
    parameters: {
      query: {
        /** @description ID of the location to start from */
        loc: string;
        /** @description ID of resource to return nearest location with content for */
        res: string;
        /** @description Whether to look for the nearest preceding (before) or subsequent (after) location with content */
        dir?: 'before' | 'after';
      };
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['LocationRead'];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  findContents: {
    parameters: {
      query?: {
        /** @description ID (or list of IDs) of resource(s) to return content data for */
        res?: string[];
        /** @description ID (or list of IDs) of location(s) to return content data for */
        location?: string[];
        /** @description Return at most <limit> items */
        limit?: number;
      };
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': (
            | components['schemas']['ApiCallContentRead']
            | components['schemas']['AudioContentRead']
            | components['schemas']['ExternalReferencesContentRead']
            | components['schemas']['ImagesContentRead']
            | components['schemas']['PlainTextContentRead']
            | components['schemas']['RichTextContentRead']
            | components['schemas']['TextAnnotationContentRead']
          )[];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  createContent: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json':
          | components['schemas']['ApiCallContentCreate']
          | components['schemas']['AudioContentCreate']
          | components['schemas']['ExternalReferencesContentCreate']
          | components['schemas']['ImagesContentCreate']
          | components['schemas']['PlainTextContentCreate']
          | components['schemas']['RichTextContentCreate']
          | components['schemas']['TextAnnotationContentCreate'];
      };
    };
    responses: {
      /** @description Successful Response */
      201: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json':
            | components['schemas']['ApiCallContentRead']
            | components['schemas']['AudioContentRead']
            | components['schemas']['ExternalReferencesContentRead']
            | components['schemas']['ImagesContentRead']
            | components['schemas']['PlainTextContentRead']
            | components['schemas']['RichTextContentRead']
            | components['schemas']['TextAnnotationContentRead'];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Conflict */
      409: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getContent: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json':
            | components['schemas']['ApiCallContentRead']
            | components['schemas']['AudioContentRead']
            | components['schemas']['ExternalReferencesContentRead']
            | components['schemas']['ImagesContentRead']
            | components['schemas']['PlainTextContentRead']
            | components['schemas']['RichTextContentRead']
            | components['schemas']['TextAnnotationContentRead'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  deleteContent: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      204: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  updateContent: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json':
          | components['schemas']['ApiCallContentUpdate']
          | components['schemas']['AudioContentUpdate']
          | components['schemas']['ExternalReferencesContentUpdate']
          | components['schemas']['ImagesContentUpdate']
          | components['schemas']['PlainTextContentUpdate']
          | components['schemas']['RichTextContentUpdate']
          | components['schemas']['TextAnnotationContentUpdate'];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json':
            | components['schemas']['ApiCallContentRead']
            | components['schemas']['AudioContentRead']
            | components['schemas']['ExternalReferencesContentRead']
            | components['schemas']['ImagesContentRead']
            | components['schemas']['PlainTextContentRead']
            | components['schemas']['RichTextContentRead']
            | components['schemas']['TextAnnotationContentRead'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  createCorrection: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['CorrectionCreate'];
      };
    };
    responses: {
      /** @description Successful Response */
      201: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['CorrectionRead'];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getCorrections: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        resourceId: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['CorrectionRead'][];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  deleteCorrection: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      204: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  findLocations: {
    parameters: {
      query?: {
        /** @description ID of location to find */
        locId?: string | null;
        /** @description ID of parent location to find children of */
        parentId?: string | null;
        /** @description ID of text to find locations for */
        textId?: string | null;
        /** @description Slug of text to find locations for */
        textSlug?: string | null;
        /** @description Structure level to find locations for */
        lvl?: number | null;
        /** @description Position value of locations to find */
        pos?: number | null;
        /** @description Alias of location(s) to find */
        alias?: null | string;
        /** @description Add full combined label to each location */
        fullLabels?: boolean;
        /** @description Return at most <limit> locations */
        limit?: number;
      };
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['LocationRead'][];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  createLocation: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['LocationCreate'];
      };
    };
    responses: {
      /** @description Successful Response */
      201: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['LocationRead'];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getPathOptionsByHeadId: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        /** @description Location ID */
        id: string;
        /** @description Wheter to handle the given location as path root or head */
        by: 'root' | 'head';
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['LocationRead'][][];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getFirstAndLastLocationsPaths: {
    parameters: {
      query: {
        /** @description Target text ID */
        txt: string;
        /** @description Structure level to find first and last locations for */
        lvl?: number;
      };
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['LocationRead'][][];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getChildren: {
    parameters: {
      query?: {
        /** @description ID of text to find locations for (required if no parent ID is given) */
        txt?: string | null;
        /** @description ID of parent location to find children of */
        parent?: string | null;
        limit?: number;
      };
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['LocationRead'][];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getLocation: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['LocationRead'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  deleteLocation: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['DeleteLocationResult'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  updateLocation: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['LocationUpdate'];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['LocationRead'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  moveLocation: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['MoveLocationRequestBody'];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['LocationRead'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getThreadMessages: {
    parameters: {
      query?: {
        /** @description ID of the thread to return messages for */
        thread?: string | null;
      };
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['UserMessageRead'][];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  sendMessage: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['UserMessageCreate'];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['UserMessageRead'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getThreads: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['UserMessageThread'][];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
    };
  };
  deleteThread: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string | 'system';
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      204: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getPlatformData: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['PlatformData'];
        };
      };
    };
  };
  updatePlatformState: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['PlatformStateUpdate'];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['PlatformStateRead'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getSegment: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['ClientSegmentRead'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  deleteSegment: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      204: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  updateSegment: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['ClientSegmentUpdate'];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['ClientSegmentRead'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  createSegment: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['ClientSegmentCreate'];
      };
    };
    responses: {
      /** @description Successful Response */
      201: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['ClientSegmentRead'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Conflict */
      409: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getAllTasksStatus: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TaskRead'][];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
    };
  };
  deleteAllTasks: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      204: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
    };
  };
  getUserTasks: {
    parameters: {
      query?: never;
      header?: {
        /** @description Comma-separated pickup keys for accessing the tasks in case they are requested by a non-authenticated user */
        'pickup-keys'?: string | null;
      };
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TaskRead'][];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  downloadTaskArtifact: {
    parameters: {
      query: {
        /** @description Pickup key for accessing the task's file artifact */
        pickupKey: string;
      };
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': unknown;
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  deleteTask: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      204: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  runPlatformCleanup: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      202: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TaskRead'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
    };
  };
  triggerResourcePrecomputation: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      202: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TaskRead'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
    };
  };
  findResources: {
    parameters: {
      query?: {
        /** @description ID of text to find resources for */
        txt?: string;
        /** @description Structure level to find resources for */
        lvl?: number;
        /** @description Type of resources to find */
        type?: string | null;
        limit?: number;
      };
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': (
            | components['schemas']['ApiCallResourceRead']
            | components['schemas']['AudioResourceRead']
            | components['schemas']['ExternalReferencesResourceRead']
            | components['schemas']['ImagesResourceRead']
            | components['schemas']['PlainTextResourceRead']
            | components['schemas']['RichTextResourceRead']
            | components['schemas']['TextAnnotationResourceRead']
          )[];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  createResource: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json':
          | components['schemas']['ApiCallResourceCreate']
          | components['schemas']['AudioResourceCreate']
          | components['schemas']['ExternalReferencesResourceCreate']
          | components['schemas']['ImagesResourceCreate']
          | components['schemas']['PlainTextResourceCreate']
          | components['schemas']['RichTextResourceCreate']
          | components['schemas']['TextAnnotationResourceCreate'];
      };
    };
    responses: {
      /** @description Successful Response */
      201: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json':
            | components['schemas']['ApiCallResourceRead']
            | components['schemas']['AudioResourceRead']
            | components['schemas']['ExternalReferencesResourceRead']
            | components['schemas']['ImagesResourceRead']
            | components['schemas']['PlainTextResourceRead']
            | components['schemas']['RichTextResourceRead']
            | components['schemas']['TextAnnotationResourceRead'];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Conflict */
      409: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  createResourceVersion: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      201: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json':
            | components['schemas']['ApiCallResourceRead']
            | components['schemas']['AudioResourceRead']
            | components['schemas']['ExternalReferencesResourceRead']
            | components['schemas']['ImagesResourceRead']
            | components['schemas']['PlainTextResourceRead']
            | components['schemas']['RichTextResourceRead']
            | components['schemas']['TextAnnotationResourceRead'];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Conflict */
      409: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getResource: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json':
            | components['schemas']['ApiCallResourceRead']
            | components['schemas']['AudioResourceRead']
            | components['schemas']['ExternalReferencesResourceRead']
            | components['schemas']['ImagesResourceRead']
            | components['schemas']['PlainTextResourceRead']
            | components['schemas']['RichTextResourceRead']
            | components['schemas']['TextAnnotationResourceRead'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  deleteResource: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      204: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  updateResource: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json':
          | components['schemas']['ApiCallResourceUpdate']
          | components['schemas']['AudioResourceUpdate']
          | components['schemas']['ExternalReferencesResourceUpdate']
          | components['schemas']['ImagesResourceUpdate']
          | components['schemas']['PlainTextResourceUpdate']
          | components['schemas']['RichTextResourceUpdate']
          | components['schemas']['TextAnnotationResourceUpdate'];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json':
            | components['schemas']['ApiCallResourceRead']
            | components['schemas']['AudioResourceRead']
            | components['schemas']['ExternalReferencesResourceRead']
            | components['schemas']['ImagesResourceRead']
            | components['schemas']['PlainTextResourceRead']
            | components['schemas']['RichTextResourceRead']
            | components['schemas']['TextAnnotationResourceRead'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  transferResource: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': string;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json':
            | components['schemas']['ApiCallResourceRead']
            | components['schemas']['AudioResourceRead']
            | components['schemas']['ExternalReferencesResourceRead']
            | components['schemas']['ImagesResourceRead']
            | components['schemas']['PlainTextResourceRead']
            | components['schemas']['RichTextResourceRead']
            | components['schemas']['TextAnnotationResourceRead'];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Conflict */
      409: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  proposeResource: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json':
            | components['schemas']['ApiCallResourceRead']
            | components['schemas']['AudioResourceRead']
            | components['schemas']['ExternalReferencesResourceRead']
            | components['schemas']['ImagesResourceRead']
            | components['schemas']['PlainTextResourceRead']
            | components['schemas']['RichTextResourceRead']
            | components['schemas']['TextAnnotationResourceRead'];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  unproposeResource: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json':
            | components['schemas']['ApiCallResourceRead']
            | components['schemas']['AudioResourceRead']
            | components['schemas']['ExternalReferencesResourceRead']
            | components['schemas']['ImagesResourceRead']
            | components['schemas']['PlainTextResourceRead']
            | components['schemas']['RichTextResourceRead']
            | components['schemas']['TextAnnotationResourceRead'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  publishResource: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json':
            | components['schemas']['ApiCallResourceRead']
            | components['schemas']['AudioResourceRead']
            | components['schemas']['ExternalReferencesResourceRead']
            | components['schemas']['ImagesResourceRead']
            | components['schemas']['PlainTextResourceRead']
            | components['schemas']['RichTextResourceRead']
            | components['schemas']['TextAnnotationResourceRead'];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  unpublishResource: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json':
            | components['schemas']['ApiCallResourceRead']
            | components['schemas']['AudioResourceRead']
            | components['schemas']['ExternalReferencesResourceRead']
            | components['schemas']['ImagesResourceRead']
            | components['schemas']['PlainTextResourceRead']
            | components['schemas']['RichTextResourceRead']
            | components['schemas']['TextAnnotationResourceRead'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  downloadResourceTemplate: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': unknown;
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  importResourceContents: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        'multipart/form-data': components['schemas']['Body_import_resource_contents_resources__id__import_post'];
      };
    };
    responses: {
      /** @description Successful Response */
      202: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TaskRead'];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  exportResourceContents: {
    parameters: {
      query?: {
        /** @description Export format */
        format?: 'json' | 'tekst-json' | 'csv';
        /** @description ID of the location to start the export's location range from */
        from?: string | null;
        /** @description ID of the location to end the export's location range at */
        to?: string | null;
      };
      header?: never;
      path: {
        /** @description ID of the resource to export */
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      202: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TaskRead'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getAnnotationAggregations: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['AnnotationAggregation'][];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getResourceCoverageData: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['ResourceCoverage'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  performSearch: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json':
          | components['schemas']['QuickSearchRequestBody']
          | components['schemas']['AdvancedSearchRequestBody'];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['SearchResults'];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  createSearchIndex: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      202: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TaskRead'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
    };
  };
  getSearchIndexInfo: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['IndexInfo'][];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
    };
  };
  exportSearchResults: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json':
          | components['schemas']['QuickSearchRequestBody']
          | components['schemas']['AdvancedSearchRequestBody'];
      };
    };
    responses: {
      /** @description Successful Response */
      202: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TaskRead'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  apiStatus: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': Record<string, never>;
        };
      };
      /** @description Service Unavailable */
      503: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
    };
  };
  getAllTexts: {
    parameters: {
      query?: {
        limit?: number;
      };
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TextRead'][];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  createText: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['TextCreate'];
      };
    };
    responses: {
      /** @description Successful Response */
      201: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TextRead'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Conflict */
      409: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  downloadStructureTemplate: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': unknown;
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  importTextStructure: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        'multipart/form-data': components['schemas']['Body_import_text_structure_texts__id__structure_post'];
      };
    };
    responses: {
      /** @description Successful Response */
      201: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': unknown;
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Conflict */
      409: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Unprocessable Entity */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
    };
  };
  updateTextStructure: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        'multipart/form-data': components['schemas']['Body_update_text_structure_texts__id__structure_patch'];
      };
    };
    responses: {
      /** @description Successful Response */
      202: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TaskRead'];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Unprocessable Entity */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
    };
  };
  insertLevel: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
        /** @description Index to insert the level at */
        index: number;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['TextLevelTranslation'][];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TextRead'];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  deleteLevel: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
        /** @description Level to delete */
        lvl: number;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TextRead'];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getText: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TextRead'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  deleteText: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      204: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  updateText: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['TextUpdate'];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TextRead'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  'users:currentUser': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['UserRead'];
        };
      };
      /** @description Missing token or inactive user. */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
    };
  };
  deleteMe: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      204: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
    };
  };
  'users:patchCurrentUser': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['UserUpdate'];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['UserRead'];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['ErrorModel'];
        };
      };
      /** @description Missing token or inactive user. */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  findUsers: {
    parameters: {
      query?: {
        /** @description Query string to search in user data */
        q?: string;
        /** @description Include active users */
        active?: boolean;
        /** @description Include inactive users */
        inactive?: boolean;
        /** @description Include verified users */
        verified?: boolean;
        /** @description Include unverified users */
        unverified?: boolean;
        /** @description Include administrators */
        admin?: boolean;
        /** @description Include regular users */
        user?: boolean;
        /** @description Page number */
        pg?: number;
        /** @description Page size */
        pgs?: number;
      };
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['UsersSearchResult'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Forbidden */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  getPublicUser: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        /** @description Username or ID */
        user: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['UserReadPublic'];
        };
      };
      /** @description Not Found */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  findPublicUsers: {
    parameters: {
      query?: {
        /** @description Query string to search in user data */
        q?: string;
        /** @description Page number */
        pg?: number;
        /** @description Page size */
        pgs?: number;
        /** @description Empty query returns all users */
        emptyOk?: boolean;
      };
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['PublicUsersSearchResult'];
        };
      };
      /** @description Unauthorized */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['TekstErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  'auth:cookie.login': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/x-www-form-urlencoded': components['schemas']['Body_auth_cookie_login_auth_cookie_login_post'];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': unknown;
        };
      };
      /** @description No Content */
      204: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['ErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  'auth:cookie.logout': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': unknown;
        };
      };
      /** @description No Content */
      204: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Missing token or inactive user. */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
    };
  };
  'register:register': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['UserCreate'];
      };
    };
    responses: {
      /** @description Successful Response */
      201: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['UserRead'];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['ErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  'verify:requestToken': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['Body_verify_request_token_auth_request_verify_token_post'];
      };
    };
    responses: {
      /** @description Successful Response */
      202: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': unknown;
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  'verify:verify': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['Body_verify_verify_auth_verify_post'];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['UserRead'];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['ErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  'reset:forgotPassword': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['Body_reset_forgot_password_auth_forgot_password_post'];
      };
    };
    responses: {
      /** @description Successful Response */
      202: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': unknown;
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  'reset:resetPassword': {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['Body_reset_reset_password_auth_reset_password_post'];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': unknown;
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['ErrorModel'];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  'users:user': {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['UserRead'];
        };
      };
      /** @description Missing token or inactive user. */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Not a superuser. */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description The user does not exist. */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  'users:deleteUser': {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      204: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Missing token or inactive user. */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Not a superuser. */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description The user does not exist. */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
  'users:patchUser': {
    parameters: {
      query?: never;
      header?: never;
      path: {
        id: string;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        'application/json': components['schemas']['UserUpdate'];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['UserRead'];
        };
      };
      /** @description Bad Request */
      400: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['ErrorModel'];
        };
      };
      /** @description Missing token or inactive user. */
      401: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Not a superuser. */
      403: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description The user does not exist. */
      404: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          'application/json': components['schemas']['HTTPValidationError'];
        };
      };
    };
  };
}
