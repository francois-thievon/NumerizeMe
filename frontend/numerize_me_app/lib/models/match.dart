class UserProfile {
  final int id;
  final String username;
  final String? firstName;
  final String? lastName;
  final int? age;
  final String? city;
  final String? bio;

  UserProfile({
    required this.id,
    required this.username,
    this.firstName,
    this.lastName,
    this.age,
    this.city,
    this.bio,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'],
      username: json['username'],
      firstName: json['first_name'],
      lastName: json['last_name'],
      age: json['age'],
      city: json['city'],
      bio: json['bio'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'first_name': firstName,
      'last_name': lastName,
      'age': age,
      'city': city,
      'bio': bio,
    };
  }

  String get displayName {
    if (firstName != null && lastName != null) {
      return '$firstName $lastName';
    }
    return username;
  }
}

class Match {
  final int matchId;
  final UserProfile user;
  final double similarityScore;
  final int unreadMessages;
  final DateTime createdAt;

  Match({
    required this.matchId,
    required this.user,
    required this.similarityScore,
    required this.unreadMessages,
    required this.createdAt,
  });

  factory Match.fromJson(Map<String, dynamic> json) {
    return Match(
      matchId: json['match_id'],
      user: UserProfile.fromJson(json['user']),
      similarityScore: json['similarity_score'].toDouble(),
      unreadMessages: json['unread_messages'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'match_id': matchId,
      'user': user.toJson(),
      'similarity_score': similarityScore,
      'unread_messages': unreadMessages,
      'created_at': createdAt.toIso8601String(),
    };
  }

  int get compatibilityPercentage => (similarityScore * 100).round();
}

class Message {
  final int id;
  final String content;
  final UserProfile sender;
  final bool isOwnMessage;
  final DateTime createdAt;
  final bool isRead;

  Message({
    required this.id,
    required this.content,
    required this.sender,
    required this.isOwnMessage,
    required this.createdAt,
    required this.isRead,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'],
      content: json['content'],
      sender: UserProfile.fromJson(json['sender']),
      isOwnMessage: json['is_own_message'],
      createdAt: DateTime.parse(json['created_at']),
      isRead: json['is_read'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'content': content,
      'sender': sender.toJson(),
      'is_own_message': isOwnMessage,
      'created_at': createdAt.toIso8601String(),
      'is_read': isRead,
    };
  }
}

class MessageCreate {
  final String content;

  MessageCreate({required this.content});

  Map<String, dynamic> toJson() {
    return {
      'content': content,
    };
  }
}

class MatchingStats {
  final int totalMatches;
  final int unreadMessages;
  final double? topSimilarity;

  MatchingStats({
    required this.totalMatches,
    required this.unreadMessages,
    this.topSimilarity,
  });

  factory MatchingStats.fromJson(Map<String, dynamic> json) {
    return MatchingStats(
      totalMatches: json['total_matches'],
      unreadMessages: json['unread_messages'],
      topSimilarity: json['top_similarity']?.toDouble(),
    );
  }
}
