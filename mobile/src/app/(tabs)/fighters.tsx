import React, { useState, useEffect, useMemo } from 'react';
import { 
    View, 
    Text, 
    StyleSheet, 
    TextInput, 
    FlatList, 
    TouchableOpacity,
    Image,
    ActivityIndicator,
    Alert 
} from 'react-native';
import { router } from 'expo-router';
import { getAllFighters } from '../../lib/api/fighter_api';
import { Fighter } from '../../types/fighter_types';

export default function FightersScreen() {
    const [fighters, setFighters] = useState<Fighter[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        loadFighters();
    }, []);

    const loadFighters = async () => {
        try {
            setLoading(true);
            const fighterData = await getAllFighters();
            setFighters(fighterData);
        } catch (error) {
            console.error('Error loading fighters:', error);
            Alert.alert('Error', 'Failed to load fighters');
        } finally {
            setLoading(false);
        }
    };

    // Filter fighters based on search query
    const filteredFighters = useMemo(() => {
        if (!searchQuery.trim()) {
            return fighters;
        }
        
        const query = searchQuery.toLowerCase().trim();
        return fighters.filter(fighter => 
            fighter.name.toLowerCase().includes(query) ||
            (fighter.nickname && fighter.nickname.toLowerCase().includes(query)) ||
            (fighter.weight_class && fighter.weight_class.toLowerCase().includes(query)) ||
            (fighter.country && fighter.country.toLowerCase().includes(query))
        );
    }, [fighters, searchQuery]);

    const handleFighterPress = (fighter_id: number) => {
        router.push({
            pathname: '/fighter-detail',
            params: {
                fighter_id: fighter_id
            }
        });
    };

    const renderFighter = ({ item }: { item: Fighter }) => (
        <TouchableOpacity 
            style={styles.fighterCard} 
            onPress={() => handleFighterPress(item.id)}
            activeOpacity={0.7}
        >
            <View style={styles.fighterImageContainer}>
                {item.image_url ? (
                    <Image 
                        source={{ uri: item.image_url }} 
                        style={styles.fighterImage}
                        defaultSource={require('../../../assets/images/icon.png')}
                    />
                ) : (
                    <View style={styles.fighterImagePlaceholder}>
                        <Text style={styles.fighterImagePlaceholderText}>
                            {item.name.charAt(0).toUpperCase()}
                        </Text>
                    </View>
                )}
            </View>
            
            <View style={styles.fighterInfo}>
                <Text style={styles.fighterName}>{item.name}</Text>
                {item.nickname && (
                    <Text style={styles.fighterNickname}>"{item.nickname}"</Text>
                )}
                <View style={styles.fighterDetails}>
                    {item.weight_class && (
                        <Text style={styles.fighterDetail}>{item.weight_class}</Text>
                    )}
                    {item.record && (
                        <Text style={styles.fighterDetail}>{item.record}</Text>
                    )}
                </View>
                {item.country && (
                    <Text style={styles.fighterCountry}>{item.country}</Text>
                )}
                {item.ranking && (
                    <Text style={styles.fighterRanking}>Ranked #{item.ranking}</Text>
                )}
            </View>
        </TouchableOpacity>
    );

    return (
        <View style={styles.container}>
            {/* Header Banner */}
            <View style={styles.header}>
                <View style={styles.headerContent}>
                    <Text style={styles.headerText}>Fighters</Text>
                </View>
                
                {/* Search Bar */}
                <View style={styles.searchContainer}>
                    <TextInput
                        style={styles.searchInput}
                        placeholder="Search fighters..."
                        value={searchQuery}
                        onChangeText={setSearchQuery}
                        autoCorrect={false}
                        autoCapitalize="none"
                    />
                </View>
            </View>

            {/* Main Content */}
            <View style={styles.mainContent}>
                {loading ? (
                    <View style={styles.loadingContainer}>
                        <ActivityIndicator size="large" color="#007AFF" />
                        <Text style={styles.loadingText}>Loading fighters...</Text>
                    </View>
                ) : filteredFighters.length === 0 ? (
                    <View style={styles.emptyContainer}>
                        <Text style={styles.emptyTitle}>
                            {searchQuery ? 'No fighters found' : 'No fighters available'}
                        </Text>
                        <Text style={styles.emptySubtitle}>
                            {searchQuery ? 
                                `No fighters match "${searchQuery}"` : 
                                'Fighter data will appear here once available'
                            }
                        </Text>
                    </View>
                ) : (
                    <FlatList
                        data={filteredFighters}
                        renderItem={renderFighter}
                        keyExtractor={(item) => item.id.toString()}
                        showsVerticalScrollIndicator={false}
                        contentContainerStyle={styles.listContainer}
                    />
                )}
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    header: {
        backgroundColor: 'white',
        paddingHorizontal: 16,
        paddingBottom: 16,
        borderBottomWidth: 1,
        borderBottomColor: '#e0e0e0',
    },
    headerContent: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: 50,
        marginBottom: 16,
    },
    headerText: {
        color: 'black',
        fontWeight: 'bold',
        fontSize: 18,
    },
    searchContainer: {
        marginBottom: 8,
    },
    searchInput: {
        backgroundColor: '#f8f8f8',
        borderWidth: 1,
        borderColor: '#e0e0e0',
        borderRadius: 8,
        paddingHorizontal: 16,
        paddingVertical: 12,
        fontSize: 16,
        color: '#333',
    },
    mainContent: {
        flex: 1,
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        paddingHorizontal: 16,
    },
    loadingText: {
        marginTop: 12,
        fontSize: 16,
        color: '#666',
    },
    emptyContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        paddingHorizontal: 16,
    },
    emptyTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 8,
        textAlign: 'center',
    },
    emptySubtitle: {
        fontSize: 16,
        color: '#666',
        textAlign: 'center',
        lineHeight: 24,
    },
    listContainer: {
        paddingHorizontal: 16,
        paddingTop: 16,
        paddingBottom: 20,
    },
    fighterCard: {
        backgroundColor: 'white',
        borderRadius: 12,
        padding: 16,
        marginBottom: 12,
        flexDirection: 'row',
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 3.84,
        elevation: 5,
    },
    fighterImageContainer: {
        width: 60,
        height: 60,
        marginRight: 16,
    },
    fighterImage: {
        width: 60,
        height: 60,
        borderRadius: 30,
        backgroundColor: '#f0f0f0',
    },
    fighterImagePlaceholder: {
        width: 60,
        height: 60,
        borderRadius: 30,
        backgroundColor: '#007AFF',
        justifyContent: 'center',
        alignItems: 'center',
    },
    fighterImagePlaceholderText: {
        color: 'white',
        fontSize: 24,
        fontWeight: 'bold',
    },
    fighterInfo: {
        flex: 1,
    },
    fighterName: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 4,
    },
    fighterNickname: {
        fontSize: 14,
        fontStyle: 'italic',
        color: '#666',
        marginBottom: 6,
    },
    fighterDetails: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        marginBottom: 4,
    },
    fighterDetail: {
        fontSize: 14,
        color: '#666',
        marginRight: 12,
        marginBottom: 2,
    },
    fighterCountry: {
        fontSize: 14,
        color: '#666',
        marginBottom: 2,
    },
    fighterRanking: {
        fontSize: 14,
        color: '#007AFF',
        fontWeight: '600',
    },
});